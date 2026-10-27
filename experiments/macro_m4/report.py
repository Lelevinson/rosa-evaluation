"""Write an honest checkpoint report; transcript review gates final conclusions."""
from .analysis import analyze
from .runner import BASE


def main():
    data = analyze()
    lines = ['# M4 execution checkpoint', '', 'Date: 2026-10-27.', '',
        'This report is generated from saved attempts. Unstarted cells are not assumed successful.', '',
        '| Backend / condition | Attempts | Primary passes | Completion incl. recovery | Requests | Known output tokens | Native ops | Task seconds |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for backend, record in data['backends'].items():
        for condition, row in record.get('conditions', {}).items():
            lines.append(f'| {backend} / {condition} | {row["attempts_with_results"]}/20 | '
                f'{row["primary_passes"]} | {row["completion_including_recovery"]} | {row["model_requests"]} | '
                f'{row["known_output_tokens"]} | {row["native_operations"]} | {row["task_wall_seconds"]:.2f} |')
        lines.extend(['', f'{backend}: {record["status"]}.'])
        if 'paired_cells' in record:
            lines.append(f'Complete paired cells: {record["paired_cells"]}/20; jointly successful pairs: '
                f'{record["matched_primary_success_pairs"]}. Engineering screen: {record["engineering_screen_pass"]}.')
            lines.append(f'Macro paired wins: {record["macro_paired_wins"]}; losses: {record["macro_paired_losses"]}.')
    lines.extend(['', f'Clarification transcripts awaiting operator review: {len(data["clarification_review_pending"])}.', '',
        'Do not treat automated clarification scores or an incomplete schedule as final acceptance. '
        'Known usage can be a lower bound when requests are unreturned or externally failed. '
        'Task wall times exclude setup, independent outside-task observations and persisted audit. '
        'Compare conditions within each backend; do not infer a causal speed ranking across models.', '',
        'M2/M3 and earlier studies remain unchanged. This study adds no planner, JTVR, memory or robot hardware.'])
    (BASE / 'M4_EXECUTION_REPORT.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__': main()
