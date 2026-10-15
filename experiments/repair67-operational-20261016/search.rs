fn search_lane()->(usize,usize){let lane=std::env::var("SEARCH_LANE").unwrap().parse::<usize>().unwrap();let lanes=std::env::var("SEARCH_LANES").unwrap().parse::<usize>().unwrap();assert_eq!(lanes,4);assert!(lane<lanes);(lane,lanes)}
fn bind_operational_args(first:u64,count:usize,lookahead:usize){assert_eq!(first,1);assert_eq!(lookahead,4096);assert_eq!(count,134217728);assert_eq!(count%lookahead,0);assert!((1..(1u64<<48)).contains(&first));let end=first.checked_add((count as u64).checked_mul(4).unwrap()).unwrap();assert!(end<=1u64<<48);}
fn window_start(first:u64,window:usize,lookahead:usize)->u64{let(lane,lanes)=search_lane();let offset=window.checked_mul(lanes).unwrap().checked_add(lane.checked_mul(lookahead).unwrap()).unwrap();let start=first.checked_add(offset as u64).unwrap();assert!((1..(1u64<<48)).contains(&start));assert!(start.checked_add(lookahead as u64).unwrap()<=1u64<<48);start}
fn stop_after()->Option<u64>{let p=std::env::var("SEARCH_STOP_FILE").unwrap();match std::fs::read_to_string(p){Ok(s)=>Some(s.trim().parse().unwrap()),Err(e)if e.kind()==std::io::ErrorKind::NotFound=>None,Err(e)=>panic!("stop marker unreadable: {e}")}}
fn record_window(start:u64,count:usize,total:usize){let p=std::env::var("SEARCH_PROGRESS_FILE").unwrap();let tmp=format!("{p}.tmp");let row=serde_json::json!({"status":"COMPLETE_WINDOW_ALL_ROWS_RECORDED","first":start,"last":start+count as u64-1,"count":count,"cumulative_worker_rows":total,"lane":search_lane().0});std::fs::write(&tmp,format!("{row}\n")).unwrap();std::fs::rename(tmp,p).unwrap();}
fn record_pass(nonce:u64){assert!((1..(1u64<<48)).contains(&nonce));let dir=std::env::var("SEARCH_PASS_DIR").unwrap();let path=std::path::Path::new(&dir).join(format!("pass-{nonce}.json"));let tmp=path.with_extension("tmp");let row=serde_json::json!({"nonce":nonce,"full_protected9024_pass":true,"selection":"lowest passing nonce after all lower intervals complete; no Toffoli selection"});std::fs::write(&tmp,format!("{row}\n")).unwrap();std::fs::rename(tmp,path).unwrap();}
fn bind_operational(){
 let path=std::env::var("ACCEPTANCE_PATH").unwrap();let expected=std::env::var("ACCEPTANCE_SHA256").unwrap();sha_check(&path,&expected);
 let row:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
 assert_eq!(row["status"],"REPAIRED67_CONDITIONAL_FULL_SOURCE_PROOF_RUNTIME_COST_ACCEPTED_FOR_ASCENDING_SEARCH");
 assert_eq!(row["candidate_stream_sha256"],"0beec42b117e5f623736c4171e156d8ffdfaeeb585285636f91bab2838e7c10b");
 assert_eq!(row["mask_sha256"],"560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d");
 assert_eq!(row["guard_sha256"],"355f9951eda21a7204a96fd391b3208e8d6e000dce6a14feb40d8f19b637f2b3");
 assert_eq!(row["conditional_theorem_sha256"],"b351ae4cbf4fab52a8248a83d517502c331a0a4291f73f0123370cad645a2c03");
 assert_eq!(row["lowest_pass_from"],1);assert_eq!(row["submission_mode"],"queue");
 assert_eq!(row["workers"],4);assert_eq!(row["threads_each"],2);assert_eq!(row["aggregate_threads_max"],8);
 assert_eq!(row["aggregate_memory_GiB_max"],48);assert_eq!(row["wall_cap_hours"],24);
 for key in["cost_gate_pass","failure_gate_pass","disabled_qualification_pass","independent_operational_review_pass","fresh_public_record_comparison_pass"]{assert_eq!(row[key],true);}
 assert!(row["measured_expected_hours_8threads"].as_f64().unwrap()<=24.0);
 let exe=std::env::current_exe().unwrap();sha_check(exe.to_str().unwrap(),row["operational_executable_sha256"].as_str().unwrap());
 let required_path="/home/hclau/ecdsa_research/repair67-operational-20261016/REQUIRED_RUNTIME_ARTIFACTS.json";
 sha_check(required_path,row["required_runtime_artifacts_manifest_sha256"].as_str().unwrap());
 let required:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(required_path).unwrap()).unwrap();
 for need in required["artifacts"].as_array().unwrap(){let path=need["path"].as_str().unwrap();let digest=need["sha256"].as_str().unwrap();assert!(row["runtime_artifacts"].as_array().unwrap().iter().any(|item|item["path"].as_str()==Some(path)&&item["sha256"].as_str()==Some(digest)));}
 for item in row["runtime_artifacts"].as_array().unwrap(){sha_check(item["path"].as_str().unwrap(),item["sha256"].as_str().unwrap());}
 search_lane();
}
#[cfg(test)]mod search_order_tests{#[test]fn interleaved_windows_partition_exact_ascending_prefix(){for lookahead in [1usize,9,4096]{let mut ranges=Vec::new();for window in 0..5{for lane in 0..4{let start=1+(window*4+lane)*lookahead;ranges.push((start,start+lookahead-1));}}ranges.sort();assert_eq!(ranges[0].0,1);for pair in ranges.windows(2){assert_eq!(pair[0].1+1,pair[1].0);}assert_eq!(ranges.last().unwrap().1,20*lookahead);}}}
