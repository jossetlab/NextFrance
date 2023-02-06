

#copy used data
cat /srv/nfs/ngs-stockage/NGS_IAI/redmine/19543/data/*.fasta  > data/allseq.fasta
cp /srv/nfs/ngs-stockage/NGS_IAI/redmine/19543/results/metadata_*.tsv data/



screen -S nextfrance

raw_seq="data/allseq.fasta"
metadata_rep="data/"
output_dir="results/"

conda activate nextstrain

snakemake -s nextstrainflu.py -p \
    -R augur_filter \
    --cores 16 \
    --conda-frontend conda \
    --config input_seq=$raw_seq \
             input_meta=$metadata_rep \
             output_rep=$output_dir


#for nextfrance FLU
cat /srv/nfs/ngs-stockage/NGS_IAI/redmine/15121/data/*.fasta /srv/nfs/ngs-stockage/NGS_IAI/redmine/15121/reference/*.fasta > data/allseq.fasta
cp /srv/nfs/ngs-stockage/NGS_IAI/redmine/15121/output/metadata_*.tsv data/
raw_seq="data/allseq.fasta"
metadata_rep="data/"
output_dir="results/"

conda activate nextstrain

snakemake -s nextstrainflu-HCL.py -p \
    -R augur_filter \
    --cores 16 \
    --conda-frontend conda \
    --config input_seq=$raw_seq \
             input_meta=$metadata_rep \
             output_rep=$output_dir



#env
# Create and activate a "nextstrain" environment
conda install -n base -c conda-forge mamba --yes
mamba create -n nextstrain
conda activate nextstrain

# Configure software channels; order is important!
conda config --env --add channels defaults
conda config --env --add channels bioconda
conda config --env --add channels conda-forge
conda config --env --set channel_priority strict
