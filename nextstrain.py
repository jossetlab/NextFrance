import os
import glob

configfile : "config/config.yaml"

#Get data location
fasta=config['input_sequence']
metadata=config['input_metadata']
thread_align=int(config['nbthreads'])

rule all:
    input:
        filtered_seq = "temp/seq_filtered.fasta"  ,
        align_fasta = "temp/seq_align.fasta" ,
        raw_tree = "temp/tree_raw.nwk" ,
        tree = "temp/tree.nwk",
        node_data = "temp/tree_branch_lengths.json" ,
        node_data_mut = "temp/tree_nt_muts.json" ,
        auspice_json = "auspice/data.json" ,  



rule augur_filter:
    input:
        sequence = fasta,
        meta = metadata

    output:
        filtered_seq = "temp/seq_filtered.fasta"  
    shell:
        "augur filter  "
        "--sequences {input.sequence} "
        "--metadata {input.meta}  "
        "--output {output.filtered_seq} " 

rule augur_align:
    input:
        filter_fasta = rules.augur_filter.output.filtered_seq 
    output:
        align_fasta = "temp/seq_align.fasta"
    threads: thread_align
    shell:
        "augur align "
        "--sequences {input.filter_fasta} "
        "--fill-gaps "
        "--nthreads {threads} "
        "--output {output} "

rule augur_raw_tree:
    input:
        align_data = rules.augur_align.output.align_fasta
    output:
        raw_tree = "temp/tree_raw.nwk"
    threads: thread_align
    shell:
        "augur tree "
        "--alignment {input} "
        "--nthreads {threads} "
        "--output {output} "

rule augur_refine:
    input:
        tree = rules.augur_raw_tree.output.raw_tree,
        alignment = rules.augur_align.output.align_fasta,
        meta = metadata
    output:
        tree = "temp/tree.nwk",
        node_data = "temp/tree_branch_lengths.json"
    shell:
        "augur refine "
        "--tree {input.tree} "
        "--alignment {input.alignment} "
        "--metadata {input.meta} "
        "--timetree "
        "--output-tree {output.tree} "
        "--output-node-data {output.node_data} "

rule augur_ancestral:
    input:
        tree = rules.augur_refine.output.tree,
        alignment = rules.augur_align.output.align_fasta
    output:
        node_data_mut = "temp/tree_nt_muts.json"
    shell:
        """
        augur ancestral \
            --tree {input.tree} \
            --alignment {input.alignment} \
            --output-node-data {output.node_data_mut}
        """        

rule augur_export:
    input:
        tree = rules.augur_refine.output.tree,
        meta = metadata,
        nt_muts = rules.augur_ancestral.output.node_data_mut,
        branch_lengths = rules.augur_refine.output.node_data,
    output:
        auspice_json = "auspice/data.json" ,  
    shell:
        "augur export v2 "
        "--tree {input.tree} "
        "--metadata {input.meta} "
        "--title 'NEXTRAIN VISUALISATION' "
        "--color-by-metadata 'location'  "
        "--node-data {input.branch_lengths} {input.nt_muts} "
        "--output {output.auspice_json} "