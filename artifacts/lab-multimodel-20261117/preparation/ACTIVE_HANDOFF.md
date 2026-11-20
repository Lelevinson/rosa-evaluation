# Completed lab comparison ? 2026-11-17

**Execution and report delivery are complete. Do not restart this experiment.** All four models finished80trials each;320total. Main audit320/320; source/config69hashes;mainarchive3233hashes; separateposthoc diagnostic4calls and23hashes,8spans. Mainrequests1008,diagnostic4,total1012; no unsafe dispatch or limit violation. Eight ambiguityattempts/model remain pending actual human semantic review; known-goal denominators36/condition. G1 is still blocked before held-out freeze.

Canonical labfolder `/media/naeem/d1/marvel proj/` has repos,models,runtime,results,evidence,reports. Detailed report deployed at `results/DETAILED_COMPARISON_REPORT.md`. Full sharebundle under `reports/ROSA_LAB_MULTIMODEL_REPORT_AND_EVIDENCE_2026-11-17.zip`. Identical local bundle is in this study's `delivery/`. Local detailed report and independently verified raw archives are in `evidence/`. Living master README updated.

Known-goalP/M:Qwen27/36,28/36;Ministral28/36,28/36;Llama0/36,0/36;Granite0/36,0/36. Llama selectedcorrectly32/36 in eachcondition, but reporting/schema errors preventedcompletion. Granite didnot emit nativecalls; one simpleposthoc probe also returnedJSONtext. QwenandMinistral differ in successfulfamilies despite same macrocount; matchedcross-model costs are in report. Do not claim modelparity or broadgeneralization.

Main archiveSHA256 fa5c14cb31ab4079317106af815bf86a810effff595fefa05f2eb6d6d51d9356. DiagnosticSHA256 e0780f578c6d328a5912176dd8ff9afa2f54df230cb07e4436ac07394a4e8f49. FinaldeliverySHA256 d872feddc03bd4e1bfa7632c6dd81761b478af844075fab62b35ad762d60a731. Finalbundle15contenthashes verified on both laptop and lab; reports deployed additively; raw main archive and69frozenfiles unchanged.

Models remain installed but are unloaded; only unrelated desktopGPUprocess remained at closeout. Owned loopback Ollama and HTTP-only Phoenix services/container remain available. Temporary sleep inhibitor released. No OAuthgrant/passwordfiles transferred. No Git commit/push made for this newstudy. Oldliveoperatornotes preserved in ACTIVE_HANDOFF_during_execution.md.
