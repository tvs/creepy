#!/usr/bin/env python
"""
Run MapReduce PageRank Calculation

Required:
s3cmd - http://s3tools.org/s3cmd
boto - http://boto.googlecode.com/
"""
import boto
import boto.emr
from boto.emr.step import StreamingStep
from boto.emr.bootstrap_action import BootstrapAction
import time
import sys
import os
import shutil

__version__ = "1.0"
__authors__ = "Bhadresh Patel <bhadresh@wsu.edu>"
__date__ = "Oct 30, 2010"

_storage = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../storage'))
_input = os.path.join(_storage, 'pagerank', 'input')
_output = os.path.join(_storage, 'pagerank', 'output')
_num_instances = 1
S3_BUCKET = "s3://wsuv.creepy/pagerank"

def initSetup():
    os.system("s3cmd del --recursive " + S3_BUCKET + " > /dev/null") # Remove bucket
    os.system("s3cmd put " + os.path.realpath(os.path.join(os.path.dirname(__file__), 'PageRank.py')) + " " + S3_BUCKET + "/ > /dev/null") # Put PageRank.py
    os.system("s3cmd put --recursive " + _input + " " + S3_BUCKET + "/ > /dev/null")

def converged(n, convergence):
    if n < 2:
        return True
    tmp = os.path.realpath(os.path.join(os.path.dirname(__file__), 'tmp'))
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)    
    os.makedirs(tmp)
    os.system("s3cmd sync " + S3_BUCKET + "/step" + str(n - 1) + "/ " + tmp + "/ > /dev/null")
    os.system("s3cmd sync " + S3_BUCKET + "/step" + str(n) + "/ " + _output + "/ > /dev/null")
    
    previous_ranks = {}
    ranks = {}
    for f in os.listdir(tmp):
        for line in open(os.path.join(tmp, f), "r"):
            (docid, pr, outlinks) = line.strip().split('\t')
            previous_ranks[docid] = float(pr)
    for f in os.listdir(_output):
        for line in open(os.path.join(_output, f), "r"):
            (docid, pr, outlinks) = line.strip().split('\t')
            ranks[docid] = float(pr)
    
    for docid in ranks:
        diff = abs(ranks[docid] - previous_ranks[docid])
        if (diff > convergence):
            return False        
    return True

def addStep(n):
    return StreamingStep(
        name='Iteration ' + str(n + 1),
        mapper=S3_BUCKET + '/PageRank.py -m',
        reducer=S3_BUCKET + '/PageRank.py -r',
        input=S3_BUCKET + '/' + ('input' if n < 1 else 'step' + str(n)),
        output=S3_BUCKET + '/step' + str(n + 1)
    )

if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser(description="PageRank Calculation",
                                   usage="usage: %prog [options]",
                                   version=__version__)
    parser.add_option('-v', '--verbose', help="Verbose Output [default: %default]", action="count", default=False)
    parser.add_option('-i', '--input', help="Initial Input [default: %default]", default=_input)
    parser.add_option('-o', '--output', help="Final Output [default: %default]", default=_output)
    parser.add_option('-s', '--steps', help="Number of Steps to run before checking for convergence [default: %default]", default=10, type='int')
    parser.add_option('-n', '--num_instances', help="Number of Instances [default: %default]", default=_num_instances, type='int')
    parser.add_option('-c', '--convergence', help="Convergence [default: %default]", default=0.0000001, type='float')
    
    (options, args) = parser.parse_args()
    
    print "### Initializing"
    initSetup()
    
    print "### Creating job flow"
    conn = boto.connect_emr()
    steps = [addStep(iteration) for iteration in range(options.steps)]
    jobid = conn.run_jobflow(
        name="Creepy PageRank Calculation", 
        log_uri=S3_BUCKET + "/logs", 
        steps=steps,
        num_instances=options.num_instances,
        keep_alive=True
    )

    print "### Created job flow", jobid

    completed = False
    jf = conn.describe_jobflow(jobid)
    while not completed:
        if jf.state == u'FAILED' or jf.state == u'ENDED':
            break
            
        time.sleep(30)
        jf = conn.describe_jobflow(jobid)
        status = ''
        if jf.state == u'RUNNING':
            for i, s in enumerate(jf.steps):
                if s.state != u'COMPLETED':
                    break
            status = "%d/%d" % (i + 1, len(jf.steps))
            print "[%s] %s %s" % (time.strftime('%H:%M:%S'), jf.state, status)
            
            if i + 1 == len(jf.steps):            
                print "### Checking for convergence"
                if converged(len(jf.steps), options.convergence):
                    completed = True
                else:
                    print "### Adding more steps to job flow", jobid
                    steps = [addStep(iteration) for iteration in range(iteration + 1, iteration + 1 + options.steps)]
                    conn.add_jobflow_steps(jobid, steps)
        else:
            print "[%s] %s" % (time.strftime('%H:%M:%S'), jf.state)
        
    print "### Terminating job flow", jobid
    conn.terminate_jobflow(jobid)

