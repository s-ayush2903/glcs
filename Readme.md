## glcs

N pbzznaq yvar gbby gb gevttre cvcryvar / wbo ba n fcrpvsvp oenapu bs n Tvgyno cebwrpg, jnvg sbe gur cvcryvar / wbo gb svavfu(guvf arrqf gb or vachg znahnyyl, nf bs abj :/)
pbyyrpg negvsnpgf naq chfu gb gur freire / ybpny znpuvar.

### ft is it?
* A command line tool which can be used to fetch artifacts from the most recent _successful_ pipeline
* It does not matter whether the pipeline ran on a branch or on a branch
* More specifically, you can provide options / preferences regarding which job's artifs you want from the fetched most recent successful pipeline
* It fetches those artifs and puts them inside a root directory `artifs`, this directory further contains dirs depending on the number of jobs you told the tool to fetch artifacts from
* These internal dirs are named as `${jobName}Artifs`, this dir contains an archived version of the artifacts fetched(basically the raw output that gitlab CI produces) and also the extracted components of that archive

### How to use / play :point_right: :point_left:
It is _crazily_ simple!
* Create a GitLab project
* Setup CI in it, obviously with artifs uploads to CI on successful jobs(cz you wanna fetch artifs :P )
* Make sure you have some jobs that are triggered on v4 API calls only, if not then your _entire_ pipeline will run(if not provided proper rules in gitlab ci file), can ignore this if you just wanna learn / try this tool out
* Obtain tokens via following instructions / refs in `reqs.py`
* `python3 reqs.py` 


Now you're ready to rock and roll :rocket:

### Info / Work left
* A work in progress
* Integrating with slack
* Read the comments in reqs.py to start using it >.<
