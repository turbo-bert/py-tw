# `tw` - A Ultra Leightweight PDF Typewriter for Python

This is a very insignificant library I personally use for PDF generation but I think it is not worth to be published on PIP but you might find it usefuly anyways.

# Dependencies

Of course and only `reportlab`.

# Example

It is brutally simple. Have `reportlab` installed of course.

    import tw
    
    pdf = tw.DINA4()
    
    # starting with page 1, not 0
    pdf.page(1).text(1, 1, 'Hello World!') # simple text to row 1.. , column 1.. from topleft
    pdf.build('output.pdf')


# Installation

Did I say lightweight? Only copy the `tw` folder (consists only the `__init__.py`) and have `reportlab` installed.
