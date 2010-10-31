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

def finished(n):
    os.system("s3cmd sync " + S3_BUCKET + "/step" + str(n + 1) + "/ " + _output + "/ > /dev/null")

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
    parser.add_option('-s', '--steps', help="Initial Number of Steps [default: %default]", default=10, type='int')
    parser.add_option('-n', '--num_instances', help="Number of Instances [default: %default]", default=_num_instances, type='int')

    (options, args) = parser.parse_args()
    
    initSetup()    
    
    conn = boto.connect_emr()
    steps = [addStep(iteration) for iteration in range(options.steps)]
    jobid = conn.run_jobflow(
        name="Creepy PageRank Calculation", 
        log_uri=S3_BUCKET + "/logs", 
        steps=steps,
        num_instances=options.num_instances
    )

    print "Created job flow", jobid

    jf = conn.describe_jobflow(jobid)
    print "%-10s %s" % ("Time", "State")
    while jf.state != u'COMPLETED' and jf.state != u'FAILED' and jf.state != u'ENDED':
        time.sleep(30)
        jf = conn.describe_jobflow(jobid)
        status = ''
        if jf.state == u'RUNNING':
            for i, s in enumerate(jf.steps):
                if s.state != u'COMPLETED':
                    break
            status = "%d/%d" % (i + 1, len(jf.steps))
        print "%-10s %s %s" % (time.strftime('%H:%M:%S'), jf.state, status)
        
    # Download output
    finished(iteration)
