from flask import Flask, request, send_file, make_response
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)


@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return {"error": "Input must be a JSON array of objects."}, 400

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        page_width, page_height = A4

        # Layout setup
        x_margin = 50
        y_start = page_height - 50
        line_height = 16
        row_spacing = 40
        col_width = (page_width - 2 * x_margin) / \
            3  # Divide page into 3 columns

        current_y = y_start
        col_index = 0  # 0, 1, 2

        for i, item in enumerate(data):
            if not isinstance(item, dict):
                continue

            # Prepare name and address
            first_name = item.get('First Name', '').strip()
            last_name = item.get('Last Name', '').strip()
            address = item.get('Address', '').lstrip(',').strip()
            full_name = f"{first_name} {last_name}".strip()

            # X position for this column
            current_x = x_margin + col_index * col_width

            # Draw name
            p.setFont("Helvetica-Bold", 12)
            p.drawString(current_x, current_y, full_name)

            # Draw address
            p.setFont("Helvetica", 11)
            p.drawString(current_x, current_y - line_height, address)

            # Move to next column
            col_index += 1

            if col_index >= 3:
                # Move to next row
                col_index = 0
                current_y -= row_spacing

                # Start new page if we're out of space
                if current_y < 100:
                    p.showPage()
                    current_y = y_start

        p.save()
        buffer.seek(0)

        response = make_response(send_file(
            buffer,
            as_attachment=True,
            download_name="labeled_data.pdf",
            mimetype='application/pdf'
        ))
        return response

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
