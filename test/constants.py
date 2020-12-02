from src.models.workflow_request import WorkflowRequest

nanopub_key = "d5JrdABbEeuatj9X3vvoXw"
expected_nanopubs = 1
empty_protocol_uri = "https://is-empty"
protocol_uri = "https://protocolexchange.researchsquare.com/article/pex-1069/v1"
test_annotations_json_path = "test/annotation_hypothesis.json"
published_trusted_uri = 'http://purl.org/np/RAdG9VXVOBq-7Ju5H085CgynfrVlwpajLb02B-W0ss8Zc'
retracted_trusted_uri = 'http://purl.org/np/RAC6FqD7TqoTCV8miMbZIx10ISVBbzm90uq3oPhSLWlnA'
published_artifact_code = 'RAdG9VXVOBq-7Ju5H085CgynfrVlwpajLb02B-W0ss8Zc'
retracted_artifact_code = 'RAC6FqD7TqoTCV8miMbZIx10ISVBbzm90uq3oPhSLWlnA'
expected_rdf = ""
workflow_request = WorkflowRequest(protocol=protocol_uri,label='my test label',description='my description',author='',nanopubs=[nanopub_key])
workflow_trusted_uri = 'http://purl.org/np/RAv7w9MrNMCvCWzZNTVXPFQQ2atF6gSuLl67Af_bYG_Qk'
workflow_retract_trusted_uri = 'http://purl.org/np/RAv7w9MrNMCvCWzZNGTRPFQQ2atF6gSuLl67Af_bYG_WB'

def is_slice_in_list(s,l):
    return set(s).issubset(set(l))

with open('test/expected_rdf.trig', 'r') as file:
    expected_rdf = file.read()
