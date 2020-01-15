# CleanWB
data wash

distributed clean
    
    python run.py --data_dir <The dir of data saved in json or txt file.> 
                    --tool_dir <Dir of the tool data.>  
                    --out_dir <The dir to store cleaned data files.>
                    --dirty_dir <The dir to store dirty cases files.>
                    
                    
    python after_rules.py --data_dir <The dir of cleand data above.> 
                    --ad_path <The path to store ad file>  
                    --out_path <The dir to store cleaned data>