import tw

pdf = tw.DINA4()
fm = tw.FlatMaker(pdf)

fm.to(10,30,1).fixbox(lines=['Box 1 Line 1', 'Box 1 Line 2'], subtitle=None, w=40, h=10)
fm.to(22,30,1).fixbox(lines=['Box 2 Line 1', 'Box 2 Line 2', 'Box 2 Line 3'], subtitle=None, w=20, h=10)
pdf.build('example2.pdf')
