# mosaic-demo
Mosaic aerial images using enblend.
Depends on enblend, gdal, and exiftools.

Make a directory, enter said directory and execute get-data.sh. That will download some sample ortho imagery from the National Geodetic Survey.

Then execute python mosaic-demo.py.

Takes about 2 minutes to blend the images into a seamless mosaic.

You MUST have the ~/.ExifTools_config in place to write the exif tags that enblend needs into the tifs gdal produces.
<pre><code>
%Image::ExifTool::UserDefined = (
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
print "LOADED!\n";
</pre></code>
