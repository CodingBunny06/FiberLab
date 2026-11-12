import ast


def test_guardian_detects_incorrect_api_signature():
    # Simulate a teammate implementing the wrong signature.
    incorrect_source = """
def calculate_numerical_aperture(n_core, cladding_index):
    return 0.0
"""

    expected_parameters = ("n_core", "n_cladding")

    module = ast.parse(incorrect_source)

    function = next(node for node in module.body if isinstance(node, ast.FunctionDef))

    actual_parameters = tuple(argument.arg for argument in function.args.args)

    assert actual_parameters != expected_parameters
    assert actual_parameters == ("n_core", "cladding_index")
