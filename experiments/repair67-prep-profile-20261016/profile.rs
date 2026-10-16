use std::sync::{OnceLock,atomic::{AtomicU64,Ordering}};
use std::time::Instant;
const LABELS:[&str;35]=[
 "startup_source_hash","startup_source_decode","startup_transfer_bind","startup_ABI_analysis",
 "startup_C_SHAKE8_context_init_unused_base","startup_whole_prefix_build_inclusive","startup_C_SHAKE8_updates_unused_base","startup_Rust_SHAKE256_updates",
 "startup_candidate_seed_diagnostics","startup_scalar_backend_inclusive","startup_scalar_fixed_table_init",
 "startup_rail_model_load","startup_zeroIR_load_bind","startup_knownmask_load_bind","startup_full_compact_compile",
 "prep_nonce_hash_packet_create_inclusive","prep_key_buffer_alloc","prep_SHAKE_key_read","prep_scalar_decode_alloc",
 "prep_curve_input_BE_pack_alloc","prep_curve_output_buffer_alloc","prep_curve_C_paircall","prep_curve_output_decode_alloc",
 "prep_curve_valid_point_filter","prep_point_vector_alloc","prep_rail_init_once","prep_rail_denominator_pack_alloc","prep_rail_flags_alloc","prep_rail_C_walk",
 "prep_rail_shadow_reference","prep_flag_candidate_collect","prep_ensure_inclusive","startup_main_to_window","prep_next_witness_inclusive","prep_packet_container_push"];
#[repr(align(64))]struct Metric{ns:AtomicU64,calls:AtomicU64,units:AtomicU64}
static ENABLED:OnceLock<bool>=OnceLock::new();static METRICS:OnceLock<Vec<Metric>>=OnceLock::new();static MAIN:OnceLock<Instant>=OnceLock::new();
fn enabled()->bool{*ENABLED.get_or_init(||std::env::var_os("PROFILE_PREP").is_some())}
fn metrics()->&'static[Metric]{METRICS.get_or_init(||(0..LABELS.len()).map(|_|Metric{ns:AtomicU64::new(0),calls:AtomicU64::new(0),units:AtomicU64::new(0)}).collect())}
pub fn begin_main(){if enabled(){metrics();let _=MAIN.set(Instant::now());}}
pub struct Span{index:usize,start:Option<Instant>}
pub fn span(index:usize)->Span{Span{index,start:enabled().then(Instant::now)}}
impl Drop for Span{fn drop(&mut self){if let Some(t)=self.start{let m=&metrics()[self.index];m.ns.fetch_add(t.elapsed().as_nanos().try_into().unwrap(),Ordering::Relaxed);m.calls.fetch_add(1,Ordering::Relaxed);}}}
pub fn measure<T>(index:usize,f:impl FnOnce()->T)->T{let _s=span(index);f()}
pub fn units(index:usize,n:u64){if enabled(){metrics()[index].units.fetch_add(n,Ordering::Relaxed);}}
pub fn end_startup(){if enabled(){let m=&metrics()[32];m.ns.store(MAIN.get().unwrap().elapsed().as_nanos().try_into().unwrap(),Ordering::Relaxed);m.calls.store(1,Ordering::Relaxed);}}
pub fn report(){if enabled(){let rows=LABELS.iter().zip(metrics()).map(|(name,m)|serde_json::json!({"name":name,"seconds":m.ns.load(Ordering::Relaxed)as f64/1e9,"calls":m.calls.load(Ordering::Relaxed),"units":m.units.load(Ordering::Relaxed)})).collect::<Vec<_>>();eprintln!("PREP_PROFILE_JSON {}",serde_json::json!({"status":"INSTRUMENTATION_ONLY_NO_AUTHORITY","timing_convention":"Startup serial elapsed; prep summed worker elapsed, inclusive clocks explicitly labeled and not additive with children or wall.","metrics":rows}));}}
