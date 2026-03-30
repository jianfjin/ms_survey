import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ms-survey")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Version flag
    parser.add_argument("--version", action="store_true", help="Print version and exit")

    # generate-synthetic command
    gen_parser = subparsers.add_parser(
        "generate-synthetic",
        help="Generate synthetic survey data",
    )
    gen_parser.add_argument(
        "--countries",
        nargs="+",
        default=["Greece", "Czech Republic"],
        help="Countries to generate data for",
    )
    gen_parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of respondents per country",
    )
    gen_parser.add_argument(
        "--output",
        default="data/synthetic_responses.parquet",
        help="Output Parquet file path",
    )
    gen_parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    gen_parser.set_defaults(func=cmd_generate_synthetic)

    # extract-template command
    template_parser = subparsers.add_parser(
        "extract-template",
        help="Create a transcription template for manual PDF data entry",
    )
    template_parser.add_argument(
        "--output",
        default="data/transcription_template.json",
        help="Output JSON file path",
    )
    template_parser.set_defaults(func=cmd_extract_template)

    # build-dataset command
    build_parser_cmd = subparsers.add_parser(
        "build-dataset",
        help="Build complete dataset from transcription files",
    )
    build_parser_cmd.add_argument(
        "inputs",
        nargs="+",
        help="Glob patterns for transcription JSON files",
    )
    build_parser_cmd.add_argument(
        "--output",
        default="data/responses.parquet",
        help="Output Parquet file path",
    )
    build_parser_cmd.add_argument(
        "--synthetic-count",
        type=int,
        default=100,
        help="Number of synthetic respondents per country (0 to disable)",
    )
    build_parser_cmd.add_argument(
        "--synthetic-countries",
        nargs="+",
        default=["Greece", "Czech Republic"],
        help="Countries for synthetic data generation",
    )
    build_parser_cmd.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for synthetic data",
    )
    build_parser_cmd.set_defaults(func=cmd_build_dataset)

    # build-excel-dataset command
    build_excel_parser = subparsers.add_parser(
        "build-excel-dataset",
        help="Build normalized dashboard dataset from Excel workbook",
    )
    build_excel_parser.add_argument(
        "--input",
        default="data/CANDLE_ Survey for Member States on National Cancer Data Node Plans(1-17).xlsx",
        help="Path to source Excel workbook",
    )
    build_excel_parser.add_argument(
        "--output-dir",
        default="data/normalized",
        help="Directory for normalized parquet outputs",
    )
    build_excel_parser.set_defaults(func=cmd_build_excel_dataset)

    # export-static-dashboard command
    export_static_parser = subparsers.add_parser(
        "export-static-dashboard",
        help="Export single-file offline HTML dashboard from normalized dataset",
    )
    export_static_parser.add_argument(
        "--dataset-dir",
        default="data/normalized",
        help="Directory containing normalized parquet dataset",
    )
    export_static_parser.add_argument(
        "--output",
        default="dist/dashboard.html",
        help="Output HTML file path",
    )
    export_static_parser.add_argument(
        "--max-payload-bytes",
        type=int,
        default=25 * 1024 * 1024,
        help="Warning threshold for embedded payload size",
    )
    export_static_parser.set_defaults(func=cmd_export_static_dashboard)

    return parser


def run() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        from ms_survey import __version__

        print(__version__)
        return 0

    if hasattr(args, "func"):
        return args.func(args)

    parser.print_help()
    return 0


def cmd_generate_synthetic(args: argparse.Namespace) -> int:
    """Generate synthetic survey data."""
    from ms_survey.synthetic import generate_synthetic_dataset
    from ms_survey.extraction import responses_to_parquet

    print(f"Generating {args.count} synthetic respondents per country...")
    print(f"Countries: {', '.join(args.countries)}")

    responses = generate_synthetic_dataset(
        countries=args.countries,
        count_per_country=args.count,
        seed=args.seed,
    )

    print(f"Generated {len(responses)} total responses")
    print(f"Writing to {args.output}...")

    responses_to_parquet(
        responses,
        output_path=args.output,
        data_source="synthetic",
    )

    print("Done!")
    return 0


def cmd_extract_template(args: argparse.Namespace) -> int:
    """Create a transcription template for manual data entry."""
    from ms_survey.extraction import create_transcription_template

    print(f"Creating transcription template at {args.output}...")
    create_transcription_template(args.output)
    print("Done! Fill in the template with data from PDFs.")
    return 0


def cmd_build_dataset(args: argparse.Namespace) -> int:
    """Build complete dataset from transcription files."""
    from ms_survey.extraction import parse_transcription_file, responses_to_parquet
    import glob

    all_responses = []

    # Parse all transcription files
    for pattern in args.inputs:
        for file_path in glob.glob(pattern):
            print(f"Parsing {file_path}...")
            response = parse_transcription_file(file_path)
            all_responses.append(response)

    print(f"Loaded {len(all_responses)} original responses")

    # Generate synthetic data if requested
    if args.synthetic_count > 0:
        from ms_survey.synthetic import generate_synthetic_dataset

        print(f"Generating {args.synthetic_count} synthetic respondents per country...")
        synthetic = generate_synthetic_dataset(
            countries=args.synthetic_countries,
            count_per_country=args.synthetic_count,
            seed=args.seed,
        )
        all_responses.extend(synthetic)
        print(f"Total responses: {len(all_responses)}")

    # Write to Parquet
    print(f"Writing to {args.output}...")
    # Note: This is simplified - in production, merge properly with data_source flags
    responses_to_parquet(all_responses, args.output, data_source="mixed")
    print("Done!")
    return 0


def cmd_build_excel_dataset(args: argparse.Namespace) -> int:
    """Build normalized dashboard dataset from source Excel workbook."""
    from ms_survey.extraction import parse_excel_workbook, write_normalized_parquet

    print(f"Parsing workbook: {args.input}")
    parsed = parse_excel_workbook(args.input)
    print(
        f"Parsed {len(parsed.respondents)} respondents, "
        f"{len(parsed.questions)} questions, {len(parsed.answers)} answers"
    )
    print(f"Writing normalized dataset to: {args.output_dir}")
    write_normalized_parquet(parsed, args.output_dir)
    print("Done!")
    return 0


def cmd_export_static_dashboard(args: argparse.Namespace) -> int:
    """Export single-file static dashboard from normalized dataset."""
    from ms_survey.static_export import export_static_dashboard_html

    print(f"Exporting static dashboard from: {args.dataset_dir}")
    result = export_static_dashboard_html(
        dataset_dir=args.dataset_dir,
        output_path=args.output,
        max_payload_bytes=args.max_payload_bytes,
    )
    print(f"Wrote: {result['output_path']}")
    print(f"Encoded payload size: {result['size_bytes']} bytes")
    if result["warnings"]:
        print("Warnings:")
        for warning in result["warnings"]:
            print(f" - {warning}")
    return 0
