# Copyright (c) 2019, Pankaj Mistry
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# * The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from PyPDF2 import PdfFileWriter, PdfFileReader
import argparse
import os
import sys
import pdb
import subprocess

'''
    Implementation for handling all pdfs in a folder
'''
def processDirOfPdf(args):
    files = os.listdir()
    opdfdir = args.opdfdir
    if args.opdfdir == "":
        os.mkdir("result")
        opdfdir = "result"
    for file in files:
        if file.endswith(".pdf"):
            input_fname = file
            output_fname = "short_"+file
            processSinglePdf(input_fname, opdfdir+"\\"+output_fname, args)
    return

'''
    Implementation for handing list of files
'''
def processListOfPdf(args):
    files = args.ipdflist.split(",")
    for file in files:
        input_fname = file
        output_fname = "short_"+file
        processSinglePdf(input_fname, output_fname, args)
    return

'''
    Implementation handling single file
'''
def openInputPDFFile(input_fname):
    isTemp = False
    try:
        origfile = PdfFileReader(open(input_fname, "rb"))
    except:
        print("Failed to parse "+input_fname)
        return 0

    if origfile.isEncrypted:
        # TODO - D.A. - 2018-11-08 - manage password protected PDFs
        try:
            origfile.decrypt('')
        except NotImplementedError:
            # If not supported, try and use qpdf to decrypt with '' first.
            # See https://github.com/mstamy2/PyPDF2/issues/378
            # Workaround for the "NotImplementedError: only algorithm code 1 and 2 are supported" issue.
            # check_executable_is_available('qpdf')
            temp_fname = 'temp_'+input_fname
            subprocess.check_call(['qpdf', '--decrypt', input_fname, temp_fname])
            origfile = PdfFileReader(open(temp_fname, "rb"))
            isTemp = True
    return (origfile, isTemp)

def processSinglePdf(input_fname, output_fname, args):
    #pdb.set_trace()
    origfile, isTemp = openInputPDFFile(input_fname)
    startPage = 0
    lastPage = origfile.getNumPages()-1
    output = PdfFileWriter()
    if args.spgn != -1:
        startPage = args.spgn

    if startPage > lastPage:
        print("for#1 "+input_fname+" startPage = "+str(startPage)+" is greater then lastPage ="+str(lastPage))
        return

    if args.epgn != -1:
        lastPage = args.epgn

    if startPage > lastPage:
        print("for#2 "+input_fname+" startPage = "+str(startPage)+" is greater then lastPage ="+str(lastPage))
        return
    #pdb.set_trace()
    for page in range(startPage, lastPage+1):
        output.addPage(origfile.getPage(page))

    # finally, write "output" to document-output.pdf
    outputStream = open(output_fname, "wb")
    output.write(outputStream)
    print("For: "+input_fname+" written to output:"+output_fname)
    origfile.stream.close()
    if isTemp == True and os.path.exists("temp_"+input_fname):
        os.remove("temp_"+input_fname)
    return

description = ("\n"
                "This utility is developed by Pankaj Mistry(pmistryusa@gmail.com)\n" 
               "The tool generates a smaller pdf from the input pdf\n"
                )

def parseArguments():
    parser = argparse.ArgumentParser(description)
    parser.add_argument("-ipdf", help="single input PDF file", type=str, default = "")
    parser.add_argument('-ipdflist', help="list of input pdf files separated by ','", type=str, default = "")
    parser.add_argument('-ipdfdir', help="input directory that contains set of pdf files[Default: Points to current director executable is in]", type=str, default = os.getcwd())
    parser.add_argument('-opdfdir', help="ouput director, where all files will be stored", type=str, default = "")
    parser.add_argument('-spgn', help="start page number", type=int, default = -1)
    parser.add_argument('-epgn', help="end page number", type=int, default = -1)
    parser.add_argument('-opdf', help="ouput pdf file, if not set it will pick a name based on input file", type=str, default = "")
    parser.add_argument('-id', help="ouput pdf file", type=str, default = "")
    args = parser.parse_args()
    return args

def verifyArgs(args):
    validcount = 0
    if args.ipdf:
        validcount += 1
    if args.ipdflist:
        validcount += 1
    if validcount == 0 and args.ipdfdir == "":
        print("Error: Can't process since no input provide, use one of -ip/-ipdflist")
        exit(-1)

    if validcount > 1:
        print("Error: Can't process since combinaton of -ip/-ipdflist/-iod is not valid")
        exit(-1)
    if args.epgn == -1 and args.spgn == -1:
        print("Error: Can't process since both -spgn and -epgn not specified, atleast specify start or end page")
        exit(-1)

    if args.spgn > args.epgn and args.epgn != -1:
        print("Error: Can't process since both -spgn is greater then -epgn ")
        exit(-1)

    if args.spgn == -1:
        print("Warning: input start page not provided, will use page 0")

    if args.epgn == -1:
        print("Warning: input end page not provided, will use last page")
        
def main():
    args = parseArguments()
    verifyArgs(args)

    cwd = os.getcwd()
    #switch the directory
    if args.ipdfdir != cwd:
        os.chdir(args.ipdfdir)

    if args.ipdf:
        opdf = args.opdf
        if opdf == "":
            opdf = "short_"+args.ipdf
        processSinglePdf(args.ipdf, opdf, args)
    elif len(args.ipdflist) != 0:
        processListOfPdf(args)
    else:#args.ipdfdir != "":
        processDirOfPdf(args)

    if cwd != os.getcwd():
        os.chdir(cwd)

if __name__== "__main__":
    main()

