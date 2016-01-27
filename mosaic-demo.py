"""
.ExifTool_config has to be in place for exiftool to write the custom tags.


"""
import os,glob
from xml.dom.minidom import parse

exifSw = 'exiftool -overwrite_original_in_place -ResolutionUnit=inches -XPosition=%s -YPosition=%s -XResolution=1 -YResolution=1 %s'
enblendSw = 'enblend -f %sx%s -a -o %s.tif @%s'
 
#############################################################################
# got to have this at ~/.ExifTool_config
def exifToolsConfig():
	etConfig ="""%Image::ExifTool::UserDefined = (
    # All EXIF tags are added to the Main table, and WriteGroup is used to
    # specify where the tag is written (default is ExifIFD if not specified):
    'Image::ExifTool::Exif::Main' => {
        0xd000 => {
            Name => 'XResolution',
            Writable => 'int16u',
        },{
            Name => 'YResolution',
            Writable => 'int16u',
        },{
            Name => 'XPosition',
            Writable => 'int16u',
        },{
            Name => 'YPosition',
            Writable => 'int16u',
        },{
            Name => 'ResolutionUnit'
            Writable => 'string',
        }
        # add more user-defined EXIF tags here...
    },
);
print "LOADED!\n";"""
	return etConfig
#############################################################################
def transSw(img):
	# check on making scanline width 78 to match nona 
	os.chdir('scanline')
	basename = os.path.basename(img).split('.')[0]
	wSw = ('gdalwarp -of VRT  -s_srs EPSG:26918 -t_srs EPSG:4326 -dstalpha -co ALPHA=YES -srcnodata "255" -dstnodata "255" ../%s.jpg %s.vrt')% (basename,basename)
	print os.getcwd()
	print wSw
	os.system(wSw)
	tSw = ('gdal_translate -co BLOCKYSIZE=256 -a_nodata "0 0 0" %s.vrt %s.tif') % (basename,basename)
	os.system(tSw)
	os.chdir('../')

def makeVrt(vrt):
	vrtSw = 'gdalbuildvrt %s.vrt *.tif' % (vrt)
	os.system(vrtSw)

def parseVrt(vrt):
	vrtBasename = os.path.basename(vrt).split('.')[0]
	enList = '%s.list' % vrtBasename
	enListFile = open(vrtBasename+'.list','w')
	vrtInfo = parse(vrt)
	GeoTransform = vrtInfo.getElementsByTagName('GeoTransform')
	for gt in GeoTransform:
		geot = gt.firstChild.data.split(',')
		pixelX = float(geot[1])
		pixelY = float(geot[5])
		# Get ULX,ULY
		ULX = float(geot[0]) + (pixelX/2)
		ULY = float(geot[3]) + (pixelY/2)
        tfw = open(vrtBasename+'.tfw','w')
        tfwTxt = '%s\n0\n0\n%s\n%s\n%s' % (pixelX,pixelY,ULX,ULY)
        tfw.write(tfwTxt)
        tfw.close()	

	VRTDataset = vrtInfo.getElementsByTagName('VRTDataset')
	for (name,value) in VRTDataset[0].attributes.items():
		if name == 'rasterXSize':
			rasterXSize = value
		if name == 'rasterYSize':
			rasterYSize = value
	print 'Mosaic size is:' ,rasterXSize, rasterYSize		
	band1 = vrtInfo.getElementsByTagName('VRTRasterBand')[0]
	sources = band1.getElementsByTagName('SimpleSource')
	if len(sources) == 0:
		sources = band1.getElementsByTagName('ComplexSource')
	
	for source in sources:
		SourceFilename = source.getElementsByTagName('SourceFilename')
		for node in SourceFilename:
			image_id = node.firstChild.data
			imageListTxt = '%s\n'%image_id
			enListFile.write(imageListTxt)
		SrcRect = source.getElementsByTagName('SrcRect')
		DstRect = source.getElementsByTagName('DstRect')
		loop = 0
		for (name, value) in DstRect[loop].attributes.items():
			#print name,value
			if name == 'xSize': # image width
				xSize = value
			if name == 'ySize': # image height
				ySize = value
			if name == 'xOff':  # x offset into mosaic
				xOff = value
			if name == 'yOff':  # y offset into mosaic
				yOff = value
		addExif = exifSw % (xOff,yOff,image_id)
		os.system(addExif)
		print image_id,xSize,ySize,xOff,yOff
	enListFile.close() 
	return rasterXSize, rasterYSize, enList, vrtBasename
def procJpgs():
	if not os.path.isdir('scanline'):
		os.mkdir('scanline')
	jpgs = glob.glob('*.jpg')
	for jpg in jpgs:
		print jpg
		transSw(jpg)
procJpgs()
os.chdir('scanline')
makeVrt('mosaic')
vrtIn = 'mosaic.vrt'
mosaicXSize, mosaicYSize, mosaicList, mosaicBasename = parseVrt(vrtIn)
enSw = enblendSw % ( mosaicXSize, mosaicYSize, mosaicBasename, mosaicList )
os.system(enSw)

