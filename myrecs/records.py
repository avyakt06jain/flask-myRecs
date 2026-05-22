import csv
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from io import StringIO

from flask import Blueprint, Response, abort, flash, g, redirect, render_template, request, url_for

from .database import get_db
from .security import login_required


records_bp = Blueprint("records", __name__, url_prefix="/records")


@records_bp.route("/")
@login_required
def dashboard():
    status = request.args.get("status", "all")
    query = request.args.get("q", "").strip()
    records = list_records(g.user["id"], status=status, query=query)
    metrics = calculate_metrics(records)
    return render_template(
        "records/dashboard.html",
        records=records,
        metrics=metrics,
        selected_status=status,
        query=query,
    )


@records_bp.route("/new", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        form, errors = parse_record_form(request.form)
        if not errors:
            get_db().execute(
                """
                INSERT INTO records (user_id, buyer_name, product_name, quantity, unit_price_cents, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    g.user["id"],
                    form["buyer_name"],
                    form["product_name"],
                    form["quantity"],
                    form["unit_price_cents"],
                    form["status"],
                    form["notes"],
                ),
            )
            get_db().commit()
            flash("Record created.", "success")
            return redirect(url_for("records.dashboard"))

        for error in errors:
            flash(error, "error")
        return render_template("records/form.html", record=form, mode="Create"), 400

    return render_template("records/form.html", record={}, mode="Create")


@records_bp.route("/<int:record_id>/edit", methods=("GET", "POST"))
@login_required
def edit(record_id):
    record = get_record_or_404(record_id)

    if request.method == "POST":
        form, errors = parse_record_form(request.form)
        if not errors:
            get_db().execute(
                """
                UPDATE records
                SET buyer_name = ?, product_name = ?, quantity = ?, unit_price_cents = ?, status = ?, notes = ?
                WHERE id = ? AND user_id = ?
                """,
                (
                    form["buyer_name"],
                    form["product_name"],
                    form["quantity"],
                    form["unit_price_cents"],
                    form["status"],
                    form["notes"],
                    record_id,
                    g.user["id"],
                ),
            )
            get_db().commit()
            flash("Record updated.", "success")
            return redirect(url_for("records.dashboard"))

        for error in errors:
            flash(error, "error")
        return render_template("records/form.html", record=form | {"id": record_id}, mode="Edit"), 400

    return render_template("records/form.html", record=record, mode="Edit")


@records_bp.route("/<int:record_id>/delete", methods=("POST",))
@login_required
def delete(record_id):
    get_record_or_404(record_id)
    get_db().execute("DELETE FROM records WHERE id = ? AND user_id = ?", (record_id, g.user["id"]))
    get_db().commit()
    flash("Record deleted.", "success")
    return redirect(url_for("records.dashboard"))


@records_bp.route("/export.csv")
@login_required
def export_csv():
    records = list_records(
        g.user["id"],
        status=request.args.get("status", "all"),
        query=request.args.get("q", "").strip(),
    )
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["buyer_name", "product_name", "quantity", "unit_price", "total", "status", "notes", "created_at"])
    for record in records:
        writer.writerow(
            [
                record["buyer_name"],
                record["product_name"],
                record["quantity"],
                cents_to_money(record["unit_price_cents"]),
                cents_to_money(record["total_cents"]),
                record["status"],
                record["notes"],
                record["created_at"],
            ]
        )
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=myrecs-records.csv"},
    )


def list_records(user_id, status="all", query=""):
    params = [user_id]
    filters = ["user_id = ?"]

    if status in {"open", "paid", "cancelled"}:
        filters.append("status = ?")
        params.append(status)

    if query:
        filters.append("(buyer_name LIKE ? OR product_name LIKE ? OR notes LIKE ?)")
        term = f"%{query}%"
        params.extend([term, term, term])

    sql = f"""
        SELECT *, quantity * unit_price_cents AS total_cents
        FROM records
        WHERE {' AND '.join(filters)}
        ORDER BY created_at DESC, id DESC
    """
    return get_db().execute(sql, params).fetchall()


def get_record_or_404(record_id):
    record = get_db().execute(
        "SELECT *, quantity * unit_price_cents AS total_cents FROM records WHERE id = ? AND user_id = ?",
        (record_id, g.user["id"]),
    ).fetchone()
    if record is None:
        abort(404)
    return record


def parse_record_form(form_data):
    errors = []
    buyer_name = form_data.get("buyer_name", "").strip()
    product_name = form_data.get("product_name", "").strip()
    notes = form_data.get("notes", "").strip()
    status = form_data.get("status", "open")

    if len(buyer_name) < 2:
        errors.append("Buyer name must be at least 2 characters.")
    if len(product_name) < 2:
        errors.append("Product name must be at least 2 characters.")
    if status not in {"open", "paid", "cancelled"}:
        errors.append("Choose a valid status.")

    try:
        quantity = int(form_data.get("quantity", ""))
        if quantity <= 0:
            raise ValueError
    except ValueError:
        quantity = 0
        errors.append("Quantity must be a positive whole number.")

    try:
        unit_price_cents = money_to_cents(form_data.get("unit_price", ""))
    except ValueError:
        unit_price_cents = 0
        errors.append("Unit price must be a valid non-negative amount.")

    return (
        {
            "buyer_name": buyer_name,
            "product_name": product_name,
            "quantity": quantity,
            "unit_price_cents": unit_price_cents,
            "unit_price": cents_to_money(unit_price_cents),
            "status": status,
            "notes": notes,
        },
        errors,
    )


def money_to_cents(value):
    try:
        amount = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError("Invalid amount") from exc
    if amount < 0:
        raise ValueError("Invalid amount")
    return int((amount * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def cents_to_money(cents):
    return f"{Decimal(cents) / Decimal('100'):.2f}"


def calculate_metrics(records):
    total_cents = sum(row["total_cents"] for row in records)
    open_cents = sum(row["total_cents"] for row in records if row["status"] == "open")
    paid_cents = sum(row["total_cents"] for row in records if row["status"] == "paid")
    return {
        "count": len(records),
        "total": cents_to_money(total_cents),
        "open": cents_to_money(open_cents),
        "paid": cents_to_money(paid_cents),
    }
