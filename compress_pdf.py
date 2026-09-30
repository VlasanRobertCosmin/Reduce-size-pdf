import pymupdf
from PIL import Image
import io
import os
import sys
import shutil
import tempfile


MAX_SIZE_MB = 10
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024


def compress_pdf(input_pdf, output_pdf):
    original_size = os.path.getsize(input_pdf)

    print("=" * 50)
    print("PDF COMPRESSOR")
    print("=" * 50)

    print(f"Fișier original: {input_pdf}")
    print(f"Dimensiune originală: {original_size / 1024 / 1024:.2f} MB")
    print(f"Limită: {MAX_SIZE_MB} MB")
    print()

    # Niveluri de compresie.
    # Începem cu o calitate mai bună și scădem treptat.
    settings = [
        (80, 2500),
        (70, 2200),
        (60, 2000),
        (50, 1800),
        (40, 1600),
        (30, 1400),
        (20, 1200),
    ]

    # Dacă PDF-ul este deja sub 10 MB
    if original_size < MAX_SIZE_BYTES:
        print("PDF-ul este deja sub 10 MB.")
        shutil.copy2(input_pdf, output_pdf)
        return

    temp_dir = tempfile.mkdtemp()

    try:

        for attempt, (quality, max_dimension) in enumerate(settings, 1):

            print(
                f"Încercarea {attempt}/{len(settings)}: "
                f"quality={quality}, max_dimension={max_dimension}"
            )

            temp_pdf = os.path.join(
                temp_dir,
                f"compressed_{attempt}.pdf"
            )

            compress_once(
                input_pdf,
                temp_pdf,
                quality,
                max_dimension
            )

            size = os.path.getsize(temp_pdf)

            print(
                f"  → Dimensiune: {size / 1024 / 1024:.2f} MB"
            )

            if size < MAX_SIZE_BYTES:

                shutil.copy2(temp_pdf, output_pdf)

                print()
                print("=" * 50)
                print("SUCCES!")
                print("=" * 50)

                print(
                    f"Dimensiune originală: "
                    f"{original_size / 1024 / 1024:.2f} MB"
                )

                print(
                    f"Dimensiune finală: "
                    f"{size / 1024 / 1024:.2f} MB"
                )

                reduction = (
                    1 - size / original_size
                ) * 100

                print(
                    f"Reducere: {reduction:.1f}%"
                )

                print()
                print(f"Fișier creat: {output_pdf}")

                return

        print()
        print("=" * 50)
        print("NU S-A PUTUT AJUNGE SUB 10 MB")
        print("=" * 50)

        # Alegem cea mai mică versiune obținută
        smallest_file = None
        smallest_size = float("inf")

        for filename in os.listdir(temp_dir):

            filepath = os.path.join(
                temp_dir,
                filename
            )

            size = os.path.getsize(filepath)

            if size < smallest_size:
                smallest_size = size
                smallest_file = filepath

        if smallest_file:
            shutil.copy2(
                smallest_file,
                output_pdf
            )

            print(
                f"Cea mai mică versiune obținută: "
                f"{smallest_size / 1024 / 1024:.2f} MB"
            )

            print(
                f"Fișier: {output_pdf}"
            )

    finally:
        shutil.rmtree(temp_dir)


def compress_once(
    input_pdf,
    output_pdf,
    quality,
    max_dimension
):

    doc = pymupdf.open(input_pdf)

    for page_number, page in enumerate(doc):

        images = page.get_images(full=True)

        for image in images:

            xref = image[0]

            try:

                image_info = doc.extract_image(xref)

                image_bytes = image_info["image"]

                # Deschidem imaginea cu Pillow
                pil_image = Image.open(
                    io.BytesIO(image_bytes)
                )

                # Convertim în RGB
                if pil_image.mode != "RGB":
                    pil_image = pil_image.convert("RGB")

                # Redimensionăm proporțional
                width, height = pil_image.size

                if width > max_dimension or height > max_dimension:

                    scale = min(
                        max_dimension / width,
                        max_dimension / height
                    )

                    new_width = int(width * scale)
                    new_height = int(height * scale)

                    pil_image = pil_image.resize(
                        (new_width, new_height),
                        Image.Resampling.LANCZOS
                    )

                # Recompresăm JPEG
                buffer = io.BytesIO()

                pil_image.save(
                    buffer,
                    format="JPEG",
                    quality=quality,
                    optimize=True
                )

                new_image = buffer.getvalue()

                # Înlocuim imaginea
                page.replace_image(
                    xref,
                    stream=new_image
                )

            except Exception as e:

                print(
                    f"  Warning: imaginea {xref} "
                    f"nu a putut fi procesată: {e}"
                )

    # Salvare optimizată
    doc.save(
        output_pdf,
        garbage=4,
        deflate=True,
        clean=True
    )

    doc.close()


if __name__ == "__main__":

    if len(sys.argv) != 3:

        print()
        print("Utilizare:")
        print(
            "python compress_pdf.py input.pdf output.pdf"
        )
        print()
        print("Exemplu:")
        print(
            "python compress_pdf.py document.pdf document_comprimat.pdf"
        )

        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]

    if not os.path.exists(input_pdf):

        print(
            f"Eroare: fișierul '{input_pdf}' nu există."
        )

        sys.exit(1)

    compress_pdf(
        input_pdf,
        output_pdf
    )