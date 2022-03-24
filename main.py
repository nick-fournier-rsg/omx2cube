import numpy as np
import openmatrix as omx
import json
import os
from os.path import splitext
import csv
from scipy.io import savemat

# Generates a cube script
class OMX2MAT:
    def __init__(self):
        with open('config.json') as f:
            config = json.load(f)

        self.in_dir = config['input location'].strip('/')
        self.out_dir = config['output location'].strip('/')

        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)

    def check_pathend(self, path):
        if path[-1] != '/':
            return path + '/'

    def generate_script(self):

        # Get list of omx files
        omx_list = [splitext(x)[0] for x in os.listdir(self.in_dir) if splitext(x)[1] == '.omx']

        # CUBE script command list, separate items are line breaks
        cmd_string = "CONVERTMAT FROM='{i}/{f}.omx' TO='{o}/{f}.mat' FORMAT='TPP' COMPRESSION=0"
        cmd_list = [[cmd_string.format(i=self.in_dir, o=self.out_dir, f=f)] for f in omx_list]

        file = open('omx2cube.s', 'w+', newline='')
        with file:
            write = csv.writer(file, escapechar="\t", quoting=csv.QUOTE_NONE)
            write.writerows(cmd_list)

    def generate_script_loop(self):

        # Get list of omx files
        omx_list = [splitext(x)[0] for x in os.listdir(self.in_dir) if splitext(x)[1] == '.omx']

        # CUBE script command list, separate items are line breaks
        script_list = [["indir = '{path}'".format(path=self.check_pathend(self.in_dir))],
                       ["outdir = '{path}'".format(path=self.check_pathend(self.out_dir))],
                       ["loop i = 0, {n}".format(n=len(omx_list)-1)]]

        # Add in the annoyingly large amount of if statements
        for i, x in enumerate(omx_list):
            if i == 0:
                script_list.append(["   if (i=0)"])
            script_list.append(["       F='{file}'".format(file=splitext(x)[0])])
            if i < (len(omx_list)-1):
                script_list.append(["   elseif (i={i})".format(i=i+1)])

        script_list.extend(
            [["   endif"],
             ["  RUN PGM=MATRIX"],
             ["      ZONES=1"],
             ["      FILEO PRINTO[1] = convert_omx_tpp.s"],
             ["      PRINT LIST=\"CONVERTMAT FROM=@indir@@F@.omx TO=@outdir@@F@.mat FORMAT=\'TPP\' COMPRESSION=0\" PRINTO=1"],
             ["  ENDRUN"],
             ["  ;run single use script"],
             ["  *Voyager.exe convert_omx_tpp.s /Start"],
             ["endloop"]]
        )

        file = open('omx2cube.s', 'w+', newline='')
        with file:
            write = csv.writer(file, escapechar="\t", quoting=csv.QUOTE_NONE)
            write.writerows(script_list)

    def convert(self):
        # Doesn't work, .mat (MATLAB) are not compatible with Cube TPP .mat files
        # Get list of omx files
        omx_list = [os.path.splitext(x) for x in os.listdir(self.in_dir) if os.path.splitext(x)[1] == '.omx']

        # Read in omx file, extract the matrices, and save them
        for fstrings in omx_list:
            omx_dat = omx.open_file(os.path.join(self.in_dir, ''.join(fstrings)), 'r')

            for mat_name in omx_dat.list_matrices():
                mat_path = os.path.join(self.out_dir, fstrings[0] + '.mat')
                savemat(mat_path, {mat_name: np.array(omx_dat[mat_name])})


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    self = OMX2MAT()
