# Conversion program for Stanford track manager dataset to voxnet compatible voxels
# Author : Shanoop Padmanabhan, Nanyang Technological University
# Cite : Voxnet, Stanford track manager
# Issue log 
# 	1. Conversion to tar encoded numpy arrays of voxels
# 	2. Voxel data does not have sufficient resolution to match input data
# 	3. Randomization of training and test data
# 	4. Include class labels in voxnet directory
#	5. Multiple frames without recognizable data in a track


import cStringIO as StringIO
import tarfile
import time
import zlib
import struct
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import glob

PREFIX = 'data/'
SUFFIX = '.npy.z'
j=0
min_x=0
min_y=0
min_z=0
max_x=-50
max_y=-50
max_z=-50

x_voxel=500
y_voxel=500
z_voxel=12

class NpyTarWriter(object):
    def __init__(self, fname):
        self.tfile = tarfile.open(fname, 'w|')

    def add(self, arr, name):

        sio = StringIO.StringIO()
        np.save(sio, arr)
        zbuf = zlib.compress(sio.getvalue())
        sio.close()

        zsio = StringIO.StringIO(zbuf)
        tinfo = tarfile.TarInfo('{}{}{}'.format(PREFIX, name, SUFFIX))
        tinfo.size = len(zbuf)
        tinfo.mtime = time.time()
        zsio.seek(0)
        self.tfile.addfile(tinfo, zsio)
        zsio.close()

    def close(self):
        self.tfile.close()


class NpyTarReader(object):
    def __init__(self, fname):
        self.tfile = tarfile.open(fname, 'r|')

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        entry = self.tfile.next()
        if entry is None:
            raise StopIteration()
        name = entry.name[len(PREFIX):-len(SUFFIX)]
        fileobj = self.tfile.extractfile(entry)
        buf = zlib.decompress(fileobj.read())
        arr = np.load(StringIO.StringIO(buf))
        return arr, name

    def close(self):
        self.tfile.close()




def visual(arr,dire):
	#reader=NpyTarReader('shapenet10_train.tar')
	#arr,name=reader.next()
	#arr,name=reader.next()
	#arr,name=reader.next()
	#arr,name=reader.next()
	#print arr
	#print arr.shape
	#print name
	x,y,z=arr.nonzero()

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	ax.scatter(x, y, z, zdir='z', c= 'red')
	plt.savefig(dire+"demo%dnv.png" %j)
	#plt.show()
	plt.close(fig)

	#print "\n\n"
def read_config (fname):
	f=open(fname,'rb')
	line=f.readline()
	if(line[:-1]=="TrackManager"):
		line=f.readline()
		serial_ver=f.readline()
		#print serial_ver
	fpointer=f.tell()
	read_track(fname,fpointer)
	

def read_track(fname,fpointer):
	temp=0
	f=open(fname,'rb')
	f.seek(fpointer)
	line=f.readline()
	while(line.strip()!=''):
		line=f.readline()
		line=f.readline()
		line=f.readline()
		label=f.readline()
		line=f.readline()
		velodyne_offset=f.readline()
		#print len(velodyne_offset)
		#print struct.unpack('d'*16,velodyne_offset[:-1])
		line=f.readline()
		num_frames=f.readline()
		#print num_frames
		fpointer=f.tell()
		dire="vis\\"+label.strip()+"\\"
		if not os.path.exists(dire):
			os.makedirs(dire)
		
		for i in range(0,int(num_frames)):
			fpointer=read_frame(fname,fpointer,dire)
		#fpointer=read_frame(fname,fpointer,dire)
		f.seek(fpointer)	

		line=f.readline()
	print min_x,min_y,min_z
	print max_x,max_y,max_z

		

def read_frame(fname,fpointer,dire):
	global j
	global min_x,min_y,min_z
	global max_x,max_y,max_z
	threshold_plot=50
	arr_x=[]
	arr_y=[]
	arr_z=[]
	f=open(fname,'rb')
	f.seek(fpointer)
	line=f.readline()
	line=f.readline()
	line=f.readline()
	line=f.readline()
	line=f.read(8)
	timestamp=struct.unpack('d',line)
	line=f.readline()
	#print timestamp
	line=f.readline()
	#print line
	robot_pose=f.read(48)
	#print len(robot_pose)
	robot_pose=struct.unpack('d'*6,robot_pose[:len(robot_pose)])
	#print robot_pose
	line=f.readline()
	line=f.readline()
	line=f.readline()
	serial_length=int(f.readline())
	#print serial_length
	data=f.read(serial_length)
	#print len(data)
	strw=struct.unpack('I',data[16:20])
	strw=strw[0]
	#print strw
	dat_mat=struct.unpack('f'*(len(data)/4),data)
	dat_mat=dat_mat[5:]
	#x,y,z=dat_mat
	#print x,y,z
	if(strw>threshold_plot):
		for i in range(0,strw/3):
			temp=dat_mat[i*3:(i*3)+3]
			if((temp[0]-robot_pose[0])<60 and (temp[0]-robot_pose[0])>-60):
				arr_x.append(temp[0]-robot_pose[0])
			if((temp[1]-robot_pose[1])<60 and (temp[1]-robot_pose[1])>-60):
				arr_y.append(temp[1]-robot_pose[1])
			arr_z.append(temp[2]-robot_pose[2])
			if((temp[0]-robot_pose[0])<min_x and (temp[0]-robot_pose[0])>-60):
				min_x=(temp[0]-robot_pose[0])
			if((temp[1]-robot_pose[1])<min_y and (temp[1]-robot_pose[1])>-60):
				min_y=(temp[1]-robot_pose[1])
			if((temp[2]-robot_pose[2])<min_z):
				min_z=(temp[2]-robot_pose[2])

			if((temp[0]-robot_pose[0])>max_x and (temp[0]-robot_pose[0])<60):
				max_x=(temp[0]-robot_pose[0])
			if((temp[1]-robot_pose[1])>max_y and (temp[1]-robot_pose[1])<60):
				max_y=(temp[1]-robot_pose[1])
			if((temp[2]-robot_pose[2])>max_z):
				max_z=(temp[2]-robot_pose[2])
			#print str(temp[0])+","+str(temp[1])+","+str(temp[2])
		voxels=np.zeros((x_voxel,y_voxel,z_voxel))
		sf_x=((x_voxel/2)-1)/((max_x-min_x))
		sf_y=((y_voxel/2)-1)/((max_y-min_y))
		sf_z=((z_voxel/2)-1)/((max_z-min_z))
		#print sf_x,sf_y
		for i in range(0,len(arr_x)):
			ix=(x_voxel/2)+(arr_x[i]*sf_x)
			iy=(y_voxel/2)+(arr_y[i]*sf_y)
			iz=(z_voxel/2)+(arr_z[i]*sf_z)
			#print arr_x[i],arr_y[i],arr_z[i]
			voxels[ix,iy,iz]=1
		#print ix,iy,iz
		#print (ix-50)/sf_x,(iy-50)/sf_y,(iz-6)/sf_z
	
		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
	
		ax.scatter(arr_x, arr_y, arr_z, zdir='z', c= 'red')
	#	#ax.set_xlim3d(0,-50)
	#	#ax.set_ylim3d(0,-44)
	#	ax.set_zlim3d(0,-2)
		plt.savefig(dire+"demo%d.png" %j)
		plt.close(fig)
		visual(voxels,dire)
		j=j+1
	line=f.readline()
 	return(f.tell())
	#plt.show()



for filename in glob.glob('C:\Users\shanoop\Downloads\stc\\natural\\ungrad_area-10-06-2010_16-12-40-cut.tm'):
	print filename
	min_x=0
	min_y=0
	min_z=0
	max_x=-50
	max_y=-50
	max_z=-50
	read_config(filename)









	
