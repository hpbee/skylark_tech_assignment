#Imports

from PIL import Image
from PIL.ExifTags import TAGS
import glob
import os
import simplekml


#Taking dataset folder name
s=input("Is this script in the same folder as image dataset (y/n) :")
if(s=='n'):
    folder=input("Input the folder containing images of dataset\n")
    os.chdir(folder)


# Adding exif data to the dictionary data
acc=0 #Number of accessed images
nd=0 #Number of images with no exif data
data={}
data['name']=[]
for img_name in glob.glob('*.JPG'):
    try:
        img=Image.open(img_name)
        info=img._getexif()
        #checking if exif data is present
        if info:
            data['name'].append(img_name)
            for (tag,value) in info.items():
                try:
                    len(value)
                    value=value[:40]
                except:
                    pass
                if not value:
                    if value!=0:value="Na"
                tagname=TAGS.get(tag,tag)
                if tagname in data.keys():
                    data[tagname].append(value)
                else:data[tagname]=['Na']*acc+[value]
        else:nd+=1;
        for item in data:
            try:data[item][acc]
            except:data[item].append("Na")
        acc+=1
    except:pass
print(acc,"accessible images found")
print(nd,"images had no exif data")

# Writing dictionary data to output csv file
output=input("Give the output csv and kml files' name (eg :output) :")
open(output+'.csv', 'w').close() #create/clear the output.csv file
for item in data:
    with open(output+'.csv','a') as f:
        f.write(str(item))
        for i in data[item]:
            f.write("\t")
            f.write(str(i))
    with open(output+'.csv','a') as f:
        f.write('\n')
print("Data written to",output+".csv file in same folder as dataset which can be opened with <tab> as delimiter")


# Function to get coordinates from gps info dictionary of image
def gps_cords(gpsdict):
    lat=lon=0.0
    d=1
    for pair in gpsdict[2]:
        lat+=(float(pair[0])/pair[1])/d
        d*=60
    d=1
    for pair in gpsdict[4]:
        lon+=(float(pair[0])/pair[1])/d
        d*=60
    if (gpsdict[1]!='N') :lat=0-lat
    if (gpsdict[3]!='E') :lon=0-lon
    try:
        alt=gpsdict[6]
        try:
            if (gpsdict[5]==1):alt=0-alt
        except:pass
    except:alt=0
    return (lon,lat,alt)


# # Converting GPSInfo of images into latitudes and longitudes and  Mapping of images to points in output kml file
diff=input("Do you want to differentiate images based on their brightness? (y/n): ")
kml=simplekml.Kml() #create new kml datatype   
names=data['name']
if (diff=='n' or diff=='N'):
    for i_no in range(acc-nd):
        point=data['GPSInfo'][i_no]
        if point=="Na":continue
        else:
            cord=gps_cords(point)
            pt=kml.newpoint(name=names[i_no][:-4],coords=[cord])
            path =os.getcwd()+'\\'+names[i_no][:-3]+'jpg'
            path=kml.addfile(path)
            #pt.style.balloonstyle.text = "<![CDATA[ <table width=100% cellpadding=0 cellspacing=0> <tr><td><img width=100% src='" + path + "' /></td></tr></table>]]>"
            pt.description = '<img src="' + names[i_no] +'" alt="picture" width="400" height="300" align="left"/>'
else:
    tres=float(input("Input Brightness threshold :"))
    for i_no in range(acc-nd):
        point=data['GPSInfo'][i_no]
        if point=="Na":continue
        else:
            cord=(gps_cords(point))
            pt=kml.newpoint(name=names[i_no][:-4],coords=[cord])
            if(data['BrightnessValue'][i_no][0]<tres*data['BrightnessValue'][i_no][1]):
                pt.style.labelstyle.color = 'ff0000ff' #red points
                pt.style.iconstyle.color = 'ff0000ff' #red points
                pt.description="Negative"
            else:
                pt.description="Positive"
            pt.description = '<img src="' + names[i_no] +'" alt="picture" width="400" height="300" align="left"/>'
    print("Yellow pins on map represents positive images ie., brightness value greater than threshold value and red pins represents negative images for given threshold brightness value of",tres)
kml.save(output+'.kml')
print('Images are mapped to',output+'.kml')
