#!/bin/bash
ROOT=`pwd`
ALY_TOOLS_PATH=/nfs/zli_gpu2/bin/developed_softwares/AlchemConvTools
auto_aly_path=/nfs/export3_25T/Bygroup_FEP_data/RBFE_JOBSUB/auto_bygroup_aly
sides='complex ligand'
system=`echo ${ROOT##*/}`
base_path=`echo ${ROOT%/*}`
echo $system $base_path
####Check if the data is already sampled
for side in $sides;do
    cd $ROOT/openmm_run/$side
    # Find directories matching the patterns and store the results in an array
    directories=(`find . -maxdepth 1 -type d \( -name 'restraints*' -o -name 'electrostatics*' -o -name 'sterics*' \)`)
    # Function to extract the numeric part for sorting
    extract_number() {
        echo "$1" | awk 'match($0, /([0-9]+)$/, a) {print a[1] + 0}'
    }
    sorted_dirs=()
    for dir in "${directories[@]}";do
        basename=$(basename "$dir")
        number=$(extract_number "$basename")
        if [[ $basename == restraints* ]]; then
            sorted_dirs+=(`printf "1~%s~%012d\n" "$basename" "$number"`)
        elif [[ $basename == electrostatics* ]]; then
            sorted_dirs+=(`printf "2~%s~%012d\n" "$basename" "$number"`)
        elif [[ $basename == sterics* ]]; then
            sorted_dirs+=(`printf "3~%s~%012d\n" "$basename" "$number"`)
        fi
    done

    IFS=$'\n' sorted_dirs=($(sort -t"~" -k1,1n -k3,3n <<< "${sorted_dirs[*]}"))
    unset IFS
    # Output the sorted results
    for dir in "${sorted_dirs[@]}"; do
        sorted_single_dir=`echo "$dir" | cut -d~ -f2`
        cd $sorted_single_dir   
        if [[ -e segment_md_finished || -e MD_Finish ]]; then
            echo `pwd` "Alchemical MD finished. Ready for analysis."
            ###Check if the csv files copied to the sample_csv_data directory
            if [ -e copy_finished ]; then
                echo `pwd` "copy have been finished."
            else
                echo `pwd` "copying sample csv files."
                if [ $sorted_single_dir == 'restraints' ]; then
                    mkdir -p sample_csv_data
                    cp state*.csv sample_csv_data
                else
                    if [ -e ana_used_data ]; then
                        python $auto_aly_path/copy_aly_sample.py
                    else
                        python $auto_aly_path/copy_sample_csv.py
                    fi
                fi
                touch copy_finished
            fi
            cd sample_csv_data
            ###Check if the free_ene.csv exist or not, if not, do the analysis
            if [ -e ./fe_cal_out/free_ene.csv ]; then
                echo "free_ene.csv exist in `pwd`. Skip analysis."
            else
                cp $auto_aly_path/input_aly.txt .
                python $ALY_TOOLS_PATH/one_end_fe_aly.py -i input_aly.txt
            fi
            ###Check if the dG_dl.png exist or not, if not, do the plotting dG_dl.png
            if [ $sorted_single_dir == 'restraints' ]; then
                echo "Will not plot the dGdl for restraints."
            else
                if [ -e ./fe_cal_out/*dG_dl.png ]; then
                    echo "dG_dl.png exist in `pwd`/fe_cal_out. Skip plotting."
                else
                    if [ -e ./fe_cal_out/free_ene.csv ]; then
                        python $auto_aly_path/dG_dlambda.py -f ./fe_cal_out/free_ene.csv -p ${sorted_single_dir}_dG_dl.png
                        mv *dG_dl.png fe_cal_out
                    fi
                fi
            fi
        else
            echo `pwd` "Alchemical MD not finished. Skip."
        fi
        cd $ROOT/openmm_run/$side
    done
done

### Collect the analysis results and generate the final dG
cd $ROOT
python $auto_aly_path/check_free_ene.py
exit_status=$?
if [ $exit_status -eq 0 ]; then
    python $auto_aly_path/get_all_fe.py
    if [ -e every_themoprocess_time.png ];then
        echo "every_themoprocess_time.png exist. Skip plotting."
    else
        python $auto_aly_path/count_simu_time.py
    fi
    if [ -e $ROOT/${system}_whole_mol_fe_time_serial.png ] && [ -e $ROOT/${system}_ligand_fe_time_serial.png ] && [ -e $ROOT/${system}_complex_fe_time_serial.png ]; then
        echo "The whole, ligand and complex fe_time_serial.png exist. Skip plotting."
    else
        python $ALY_TOOLS_PATH/bygroup_combine_time_serials_data.py -s "$system" -p "$base_path"
    fi
    if [ -e $ROOT/${system}_report.pdf ]; then
        echo "The report.pdf exist. Skip report generation."
    else
        python $auto_aly_path/gen_report.py
    fi
    if [ -e $ROOT/final_fe_data.csv ] && [ -e $ROOT/${system}_report.pdf ]; then
        touch $ROOT/aly_finished
    fi
else
    echo "There is no free_ene.csv in the some directories. Skip analysis and report generation."
fi
