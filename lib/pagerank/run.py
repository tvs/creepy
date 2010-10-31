#!/usr/bin/env python
"""
Run MapReduce PageRank Calculation

Required:
s3cmd - http://s3tools.org/s3cmd
boto - http://boto.googlecode.com/ (required 2.0b3 or higher)
"""

import time
import boto
from boto.emr.step import StreamingStep
import os
import shutil

__version__ = "1.0"
__authors__ = "Bhadresh Patel <bhadresh@wsu.edu>"
__date__ = "Oct 30, 2010"

_storage = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../storage'))
_input = os.path.join(_storage, 'pagerank', 'input')
_output = os.path.join(_storage, 'pagerank', 'output')
_num_instances = 1
_s3bucket = "s3://wsuv.creepy/pagerank"
_verbose = False

def init_setup():
    """Initialize - upload code and input"""
    os.system("s3cmd del --recursive " + _s3bucket + " > /dev/null") # Remove bucket
    os.system("s3cmd put " + os.path.realpath(os.path.join(os.path.dirname(__file__), 'PageRank.py')) + " " + _s3bucket + "/ > /dev/null") # Put PageRank.py
    os.system("s3cmd put --recursive " + _input + " " + _s3bucket + "/ > /dev/null")

def converged(n, convergence):
    """Check for convergence, download last two output and compare pagerank diff"""
    if n < 2:
        return True

    os.system("rm -rf " + _output + "/*")
    tmp = os.path.realpath(os.path.join(os.path.dirname(_output), 'tmp'))
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    os.makedirs(tmp)

    os.system("s3cmd sync " + _s3bucket + "/step" + str(n - 1) + "/ " + tmp + "/ > /dev/null")
    os.system("s3cmd sync " + _s3bucket + "/step" + str(n) + "/ " + _output + "/ > /dev/null")

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

def get_step(n):
    """Returns new streamming step"""
    return StreamingStep(
        name='Iteration ' + str(n + 1),
        mapper=_s3bucket + '/PageRank.py -m',
        reducer=_s3bucket + '/PageRank.py -r',
        input=_s3bucket + '/' + ('input' if n < 1 else 'step' + str(n)),
        output=_s3bucket + '/step' + str(n + 1)
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
    _input = options.input
    _output = options.output
    _verbose = options.verbose
    
    print "### Initializing"
    init_setup()

    print "### Creating job flow"
    conn = boto.connect_emr()
    steps = [get_step(iteration) for iteration in range(options.steps)]
    jobid = conn.run_jobflow(
        name="Creepy PageRank Calculation",
        log_uri=_s3bucket + "/logs",
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
                    steps = [get_step(iteration) for iteration in range(iteration + 1, iteration + 1 + options.steps)]
                    conn.add_jobflow_steps(jobid, steps)
        else:
            print "[%s] %s" % (time.strftime('%H:%M:%S'), jf.state)

    if completed:
        print "### Executing final step to generate pagerank data file"
        finalstep = StreamingStep(
            name='Final Step',
            mapper=_s3bucket + '/PageRank.py -f -m',
            reducer=_s3bucket + '/PageRank.py -f -r',
            input=_s3bucket + '/step' + str(iteration + 1),
            output=_s3bucket + '/output'
            #,step_args=['jobconf', 'mapred.reduce.tasks=1']
        )
        conn.add_jobflow_steps(jobid, finalstep)
        jf = conn.describe_jobflow(jobid)
        while jf.steps[-1].state != u'COMPLETED':
            print "[%s] %s" % (time.strftime('%H:%M:%S'), jf.steps[-1].state)
            time.sleep(30)
            jf = conn.describe_jobflow(jobid)

        print "### Job flow completed"
        print "### Downloading final output"
        os.system("rm -rf " + _output + "/*")
        os.system("s3cmd sync " + _s3bucket + "/output/ " + _output + "/ > /dev/null")
        print "### Final output is in:", _output

    print "### Terminating job flow", jobid
    conn.terminate_jobflow(jobid)
