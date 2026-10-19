from pyshacl import validate
from rdflib import Graph, Namespace, Literal, RDF

ORIGO = Namespace("https://nexus.cleantechhub.net/data/ontology#")


def make_parcel(land_cover: str, jrc_status: str) -> Graph:
    g = Graph()
    g.bind("origo", ORIGO)
    parcel = ORIGO["test_parcel_001"]
    g.add((parcel, RDF.type, ORIGO.FarmParcel))
    g.add((parcel, ORIGO.ideamLandCoverClass, Literal(land_cover)))
    g.add((parcel, ORIGO.jrcMappingStatus, Literal(jrc_status)))
    return g


def test_agroforestry_warning():
    """cafe_sombra + mapped → should produce Warning, not Violation"""
    data = make_parcel("cafe_sombra", "mapped")
    shapes = Graph().parse("/opt/data-platform/shacl/shapes/agroforestry_canopy.ttl", format="turtle")
    conforms, results_graph, results_text = validate(data, shacl_graph=shapes)
    print(results_text)
    assert "Warning" in results_text
    assert "Violation" not in results_text, "cafe_sombra should be Warning, not Violation"
    print("PASS: cafe_sombra correctly triggers sh:Warning")


def test_disputed_jrc_violation():
    """pasture + disputed → should produce Violation"""
    data = make_parcel("pasture", "disputed")
    shapes = Graph().parse("/opt/data-platform/shacl/shapes/agroforestry_canopy.ttl", format="turtle")
    conforms, results_graph, results_text = validate(data, shacl_graph=shapes)
    print(results_text)
    assert "Violation" in results_text
    print("PASS: disputed JRC status correctly triggers sh:Violation")


def test_clean_parcel_conforms():
    """pasture + mapped → should fully conform (no flags)"""
    data = make_parcel("pasture", "mapped")
    shapes = Graph().parse("/opt/data-platform/shacl/shapes/agroforestry_canopy.ttl", format="turtle")
    conforms, results_graph, results_text = validate(data, shacl_graph=shapes)
    assert conforms is True
    print("PASS: clean parcel conforms")


if __name__ == "__main__":
    test_agroforestry_warning()
    test_disputed_jrc_violation()
    test_clean_parcel_conforms()
    print("\nAll Track D tests passed.")
