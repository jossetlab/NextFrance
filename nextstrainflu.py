import os
import glob

configfile : "config/config.yaml"

fasta=config['input_seq']

metadata=config['input_meta']
if (metadata[-1] != "/"):
	metadata=metadata+"/"

outputdir=config['output_rep']
if (outputdir[-1] != "/"):
	outputdir=outputdir+"/"


(SUBTYPE)=["H1N1","H3N2","BVIC"]

rule all:
    input:
        #filtered_seq = expand(outputdir + "temp/seq_filtered_{subtype}.fasta",subtype=SUBTYPE),
        #align_fasta = expand( outputdir + "temp/seq_align_{subtype}.fasta" ,subtype=SUBTYPE),
        #raw_tree = expand( outputdir + "temp/tree_raw_{subtype}.nwk",subtype=SUBTYPE),
        #tree = expand( outputdir + "temp/tree_{subtype}.nwk",subtype=SUBTYPE),
        #node_data = expand( outputdir + "temp/tree_branch_lengths_{subtype}.json",subtype=SUBTYPE),
        #node_data_mut = expand( outputdir + "temp/tree_nt_muts_{subtype}.json",subtype=SUBTYPE),
        #node_data_aa = expand( outputdir + "temp/aa_muts_{subtype}.json",subtype=SUBTYPE),
        #node_traits = expand( outputdir + "temp/traits_{subtype}.json",subtype=SUBTYPE),
        auspice_json = expand( "auspice/nextfrance_FLUSS-{subtype}.json", subtype=SUBTYPE),

rule remove_dupp:
    input:
        sequence = fasta,
    output:
        uniqseq =  outputdir + "temp/uniqseq_{subtype}.fasta" 
    shell:
        """
        seqkit rmdup --by-name {input.sequence} > {output.uniqseq}
        """     

rule augur_filter:
    input:
        sequence = rules.remove_dupp.output.uniqseq,
        meta = metadata + "metadata_{subtype}.tsv"
    output:
        filtered_seq = outputdir + "temp/seq_filtered_{subtype}.fasta"  
    shell:
        """
        augur filter \
        --sequences {input.sequence} \
        --metadata {input.meta}  \
        --min-date 2019-12-01 \
        --max-date 2020-07-30 \
        --non-nucleotide \
        --group-by country \
        --sequences-per-group 20 \
        --include-where dataset=GIHSN \
        --output {output.filtered_seq} 
        """ 

rule augur_align:
    input:
        filter_fasta = rules.augur_filter.output.filtered_seq ,
        ref = "reference/{subtype}_HA.gb"
    output:
        align_fasta = outputdir + "temp/seq_align_{subtype}.fasta"
    threads: 10
    shell:
        """
        augur align \
            --sequences {input.filter_fasta} \
            --fill-gaps \
            --nthreads {threads} \
            --reference-sequence {input.ref} \
            --remove-reference \
            --output {output} 
        """

rule augur_raw_tree:
    input:
        align_data =  rules.augur_align.output.align_fasta
    output:
        raw_tree = outputdir + "temp/tree_raw_{subtype}.nwk"
    threads: 10
    shell:
        """
        augur tree \
            --alignment {input} \
            --nthreads {threads} \
            --output {output} 
        """

rule augur_refine:
    input:
        tree = rules.augur_raw_tree.output.raw_tree,
        alignment = rules.augur_align.output.align_fasta,
        meta = metadata + "metadata_{subtype}.tsv"
    output:
        tree = outputdir + "temp/tree_{subtype}.nwk",
        node_data = outputdir + "temp/tree_branch_lengths_{subtype}.json"
    threads: 10
    shell:
        """
        augur refine \
            --tree {input.tree} \
            --alignment {input.alignment} \
            --metadata {input.meta} \
            --timetree \
            --output-tree {output.tree} \
            --output-node-data {output.node_data} 
        """

rule augur_ancestral:
    input:
        tree = rules.augur_refine.output.tree,
        alignment = rules.augur_align.output.align_fasta
    output:
        node_data_mut = outputdir + "temp/tree_nt_muts_{subtype}.json",
    shell:
        """
        augur ancestral \
            --tree {input.tree} \
            --alignment {input.alignment} \
            --inference "joint" \
            --output-node-data {output.node_data_mut}
        """        

rule augur_translate:
    input:
        tree = rules.augur_refine.output.tree,
        nt_muts = rules.augur_ancestral.output.node_data_mut,
        ref = "reference/{subtype}_HA.gb"
    output:
        node_data = outputdir + "temp/aa_muts_{subtype}.json"        
    shell:
        """
        augur translate \
            --tree {input.tree} \
            --ancestral-sequences {input.nt_muts} \
            --reference-sequence {input.ref} \
            --output-node-data {output.node_data} 
        """

rule augur_traits:
    message:
        "Infering ancestral traits for given column."
    input:
        tree = rules.augur_refine.output.tree,
        meta = metadata + "metadata_{subtype}.tsv"
    output:
        node_traits = outputdir + "temp/traits_{subtype}.json"
    shell:
        """
        augur traits \
            --tree {input.tree} \
            --metadata {input.meta} \
            --output-node-data {output.node_traits} \
            --columns "country" \
            --confidence
        """

rule augur_clades:
    message: "Annotating clades"
    input:
        tree = rules.augur_refine.output.tree,
        nt_muts = rules.augur_ancestral.output.node_data_mut,
        aa_muts = rules.augur_translate.output.node_data,
        clades = "reference/clade_{subtype}_HA.tsv"
    output:
        clades = outputdir + "temp/clades_{subtype}.json"
    shell:
        """
        augur clades \
            --tree {input.tree} \
            --mutations {input.nt_muts} {input.aa_muts} \
            --clades {input.clades} \
            --output {output.clades}
        """


rule augur_export:
    input:
        tree = rules.augur_refine.output.tree,
        meta = metadata + "metadata_{subtype}.tsv",
        nt_muts = rules.augur_ancestral.output.node_data_mut,
        branch_lengths = rules.augur_refine.output.node_data,
        aa_mut = rules.augur_translate.output.node_data,
        traits = rules.augur_traits.output.node_traits,
        clades = rules.augur_clades.output.clades ,
    output:
        auspice_json = "auspice/nextfrance_FLUSS-{subtype}.json"  ,  
    shell:
        """
        augur export v2 \
        --tree {input.tree} \
        --metadata {input.meta} \
        --title 'NEXTRAIN {wildcards.subtype} HA SEGMENT VISUALISATION' \
        --color-by-metadata 'country' 'dataset'  \
        --node-data {input.branch_lengths} {input.nt_muts} {input.traits} {input.aa_mut} {input.clades} \
        --output {output.auspice_json} 
        """