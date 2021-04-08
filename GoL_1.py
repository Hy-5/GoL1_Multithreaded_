import sys, getopt, os, copy, time, threading
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

#from multiprocessing import Process

#Pycallgraph integration
'''with PyCallGraph(output=GraphvizOutput()):
    code_to_profile()'''

#Creating input matrix iMat as a list() of size l(number of rows)
def matCreation():
    global iMat
    iMat=[[]]*l

'''Populating input matrix with input file.
argument t is thread number, mat is the sub list that gets appended to input list iMat to make input list a list of list
for each thread t, reads line t of the input file and adds it to inputmatrix[row t]'''
def iMatPop(t, mat):
    if (t==l-1):
        global threadEnd
        threadEnd=1
        #print("reached end of matrix")
    if (t>l-1):
        #print("thread unutilized")
        return
    lineToRead=lines[t]
    mat=copy.deepcopy(list(lineToRead))


    global iMat
    iMat[t]=copy.deepcopy(mat)
    mat.clear()

'''Populating output matrix
For each thread t, reads line t of the input matrix and checks the number of neighboors neigh. Then set corresponding cell in output matrix alive or dead'''
def oMatPop(t, neigh):
    if (t==l-1):
        global oMatEnd
        oMatEnd=1
    if (t>l-1):
        return


    for j in range(x-1):
        neigh=neighCount(t,j)
        if (iMat[t][j]=="."):
            if((neigh%2)==0) and (neigh>0):
                oMat[t][j]="O"
            else:
                oMat[t][j]="."
        elif (iMat[t][j]=="O"):
            if((neigh!=2) and (neigh!=3) and (neigh!=4)):
                oMat[t][j]="."
            else:
                oMat[t][j]="O"


#Returns the number of living neighboors to the output matrix population function (oMatPop())
def neighCount(i,j):
    global iMat
    count=0
    #handling wraparounds
    if (i==0):
        top=l-1
    else:
        top=i-1

    if (j==0):
        left=x-2
    else:
        left=j-1

    if(i==(l-1)):
        bottom=0
    else:
        bottom=i+1

    if(j==(x-2)):
        right=0
    else:
        right=j+1

    #counting alive neighboors
    #print("------------------i ", i)
    #print("------------------j ", j)
    #print("------------------top ", top)
    #print("------------------bottom ", bottom)
    #print("------------------left ", left)
    #print("------------------right ", right)

    if (iMat[top][j]=="O"):
        count=count+1
    if (iMat[bottom][j]=="O"):
        count=count+1
    if (iMat[i][left]=="O"):
        count=count+1
    if (iMat[i][right]=="O"):
        count=count+1
    if (iMat[top][left]=="O"):
        count=count+1
    if (iMat[top][right]=="O"):
        count=count+1
    if (iMat[bottom][left]=="O"):
        count=count+1
    if (iMat[bottom][right]=="O"):
        count=count+1

    #print("iMat[",i,"][",j,"] has ",count," alive neighboors")
    return count


#prints the content of the last output matrix in the output file
def outCreate():
    for i in range(l):
        for j in range(x-1):
            g.write(oMat[i][j])
        g.write("\n")
        

#iterates n times through the program, defaults to 100
def iterations():
    neighCount=[[]]*int(threadCount)
    threads=list()
    global oMat
    global iMat
    stop=0

    while stop!=100:

        #multithreading oMatPop
        z=0
        global oMatEnd
        oMatEnd=0
        while (oMatEnd==0):
            for i in range (int(threadCount)):
                t=threading.Thread(target=oMatPop, args=((i+z), neighCount[i+z]))
                threads.append(t)
                t.start()
            if oMatEnd==0:
                z=z+int(threadCount)
                for i in range(z):
                    neighCount.append([])
                neighCount.append([]*z)
        for t in threads:
            t.join()
        threads.clear()

        iMat.clear()
        iMat=copy.deepcopy(oMat)
        stop=stop+1


def main(argv):
    start=time.time()
    print("Project :: R11382145")
    inputfile = ''
    outputfile = ''
    global threadCount
    threadCount=1
    
    try:
        opts, args = getopt.getopt(argv,"i:o:t:",["ifile=","ofile=","tNumber="])
    except:
        print("Invalid command\nCorrect format: python3 <projectname.py> -i <path_to_input_file> -o <path_to_ouput_file> -t <optional_number_of_threads_defaults_to_1>")
        exit(1)

    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-t", "--tNumber"):
            threadCount=arg
    try:
        global f
        f=open(inputfile, "r")
    except FileNotFoundError:
        print("Input file does not exist")
        exit(1)
    if outputfile=='':
        print("Output file not specified")
        exit(1)

    #print ("----------------------------------\nTESTING INPUT ARGS ARE CORRECT")
    #print ("Input file is ", inputfile)
    #print ("Output file is ", outputfile)
    #print ("NUmber of threads ", threadCount)
    #print("-----------------------------------")

    if os.path.exists(outputfile):
        os.remove(outputfile)
    global g
    g=open(outputfile,'a')
    global l
    l=len(f.readlines())
    f.seek(0,0)
    s=len(f.read())
    global x
    x=int(s/l)
    f.seek(0,0)
    global lines
    lines=f.readlines()

    f.seek(0,0)
    matCreation()
    mat =[[]]*int(threadCount)
    global threadEnd
    threadEnd=0
    threads=list()
    y=0
    
    #reads input file and fills input matrix accordingly
    #multithreading iMatPop()
    while (threadEnd==0):
        for i in range (int(threadCount)):
            t=threading.Thread(target=iMatPop, args=((i+y), mat[i+y]))
            threads.append(t)
            t.start()
        if threadEnd==0:
            y=y+int(threadCount)
            for i in range(y):
                mat.append([])
            mat.append([]*y)
            
    for t in threads:
        t.join()
    threads.clear()

    global oMat
    oMat=copy.deepcopy(iMat)

    iterations()
    outCreate()

    #printing wall clock time
    end=time.time()
    print(end-start)


if __name__== '__main__':
    main(sys.argv[1:])