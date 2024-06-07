#!/bin/bash
if [ -L $0 ]; then
    BASE_DIR=`dirname $(readlink $0)`
else
    BASE_DIR=`dirname $0`
fi
basepath=$(cd $BASE_DIR; pwd)
path_file="$basepath/sys_to_reini.txt"

# 读取文件的每一行并遍历
for path in $(cat "$path_file"); do
    # 进入对应的路径
    cd "$path" || continue
    
    sh $basepath/single_reinitialize.sh 
    # 返回到原始目录
    cd - > /dev/null
done
