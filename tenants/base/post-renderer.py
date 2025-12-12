#!/opt/homebrew/bin/python3
import sys
import yaml
import os


def merge_values(helm_output, new_values):

    # Load Helm output
    helm_data = list(yaml.safe_load_all(helm_output))
    #print(helm_data)
    # Load additional values
    with open(new_values, 'r') as file:
        config_data = yaml.safe_load(file)
        yaml_list = list(config_data['data'].values())
        config_yaml = yaml.safe_load(yaml_list[0])
        #print(config_yaml.get('apiServer', {}).get('image'))
    
    # Example of merging values
    for doc in helm_data:
        #print(doc)
        if not doc is None:
            doc['metadata']['namespace'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml.get('project', {}).get('name')
            kind = doc['kind']
            #print(kind)
            # Handling for DataSciencePipelinesApplication
            if kind == 'DataSciencePipelinesApplication':
                #doc['metadata']['name'] = 'dspa'
                spec = doc['spec']
                # API Server updates
                api_server = spec['apiServer']
                #print(config_yaml['apiServer']['deploy'])
                #print(config_yaml.get('apiServer', {}).get('image'))
                api_server.update({
                    'deploy': config_yaml.get('apiServer', {}).get('deploy'),
                    
                    
                    'resources': config_yaml.get('apiServer', {}).get('resources'),
                    'cABundle': {
                        'configMapKey': config_yaml.get('apiServer', {}).get('cABundle', {}).get('configMapKey'),
                        'configMapName': config_yaml.get('apiServer', {}).get('cABundle', {}).get('configMapName')
                    }
                })
                #print(api_server)

                # Workflow Controller updates
                workflow_controller = spec['workflowController']
                workflow_controller.update({
                    'deploy': config_yaml.get('workflowController', {}).get('deploy'),
                    'customConfig': config_yaml.get('workflowController', {}).get('customConfig')
                })

                # Persistence Agent updates
                persistence_agent = spec['persistenceAgent']
                persistence_agent.update({
                    'deploy': config_yaml.get('persistenceAgent', {}).get('deploy'),
                    
                    'numWorkers': config_yaml.get('persistenceAgent', {}).get('numWorkers'),
                    'resources': config_yaml.get('persistenceAgent', {}).get('resources')
                })

                # Scheduled Workflow updates
                scheduled_workflow = spec['scheduledWorkflow']
                scheduled_workflow.update({
                    'deploy': config_yaml.get('scheduledWorkflow', {}).get('deploy'),
                    
                    'cronScheduleTimezone': config_yaml.get('scheduledWorkflow', {}).get('cronScheduleTimezone'),
                    'resources': config_yaml.get('scheduledWorkflow', {}).get('resources')
                })

                # MLPipeline UI updates
                mlpipeline_ui = spec['mlpipelineUI']
                mlpipeline_ui.update({
                    'deploy': config_yaml.get('mlpipelineUI', {}).get('deploy'),

                    'resources': config_yaml.get('mlpipelineUI', {}).get('resources'),
                    'configMap': config_yaml.get('mlpipelineUI', {}).get('configMap')
                })

                # Metadata Management (MLMD) updates
                mlmd = spec['mlmd']
                mlmd.update({
                    'deploy': config_yaml.get('mlmd', {}).get('deploy'),
                    'envoy': {

                        'resources': config_yaml.get('mlmd', {}).get('envoy', {}).get('resources')
                    },
                    'grpc': {

                        'port': config_yaml.get('mlmd', {}).get('grpc', {}).get('port'),
                        'resources': config_yaml.get('mlmd', {}).get('grpc', {}).get('resources')
                    }
                })

                # Database configuration updates
                database = spec['database']
                database.update({
                    'disableHealthCheck': config_yaml.get('database', {}).get('disableHealthCheck'),
                    'customExtraParams': config_yaml.get('database', {}).get('customExtraParams')
                    })
                if not database['mariaDB']:
                    database.update({
                    'externalDB': {
                        'host': 'hippo-primary.postgres-operator.svc',
                        'port': '5432',
                        'username': 'dspa',
                        'pipelineDBName': 'mlpipelineDB',
                        'passwordSecret': {
                            'name': 'hippo-pguser-dspa',
                            'key': 'password'
                        }
                    }
                })

                # Object Storage updates
                object_storage = spec['objectStorage']
                object_storage.update({
                    'disableHealthCheck': config_yaml.get('objectStorage', {}).get('disableHealthCheck'),
                    'externalStorage': {
                        'scheme': config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('scheme'),
                        'secure': config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('secure'),
                        'host': config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('host'),
                        'port': str(config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('port')),
                        'bucket': config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('bucket'),
                        's3CredentialsSecret': {
                            'secretName': config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('s3CredentialsSecret', {}).get('secretName'),
                            'accessKey': config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('s3CredentialsSecret', {}).get('accessKey'),
                            'secretKey': config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('s3CredentialsSecret', {}).get('secretKey')
                        }
                    }
                })
            elif kind == 'PersistentVolumeClaim':
                #doc['metadata']['namespace'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml.get('project', {}).get('name')
                if doc['metadata']['annotations']['openshift.io/description'] == 'mc Storage':
                    doc['metadata']['annotations']['openshift.io/display-name'] = config_yaml.get('project', {}).get('name')+'-'+config_yaml.get('project', {}).get('notebook', {}).get('name')+'-mc-pvc'
                    doc['metadata']['name'] = config_yaml.get('project', {}).get('name')+'-'+config_yaml.get('project', {}).get('notebook', {}).get('name')+'-mc-pvc'
                else:
                    doc['metadata']['annotations']['openshift.io/display-name'] = config_yaml.get('project', {}).get('name')+'-'+config_yaml.get('project', {}).get('notebook', {}).get('type')+'-'+config_yaml.get('project', {}).get('notebook', {}).get('name')+'-workbench-pvc'
                    doc['metadata']['name'] = config_yaml.get('project', {}).get('name')+'-'+config_yaml.get('project', {}).get('notebook', {}).get('type')+'-'+config_yaml.get('project', {}).get('notebook', {}).get('name')+'-workbench-pvc'

            elif kind == 'SealedSecret':
                #doc['metadata']['namespace'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml.get('project', {}).get('name')
                doc['spec']['template']['metadata']['namespace'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml.get('project', {}).get('name')

            elif kind == 'Job' and doc is not None:
                if doc['metadata']['name'] == 'create-minio-bucket':
                    #doc['metadata']['namespace'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml.get('project', {}).get('name')
                    doc['spec']['template']['spec']['serviceAccountName'] = config_yaml.get('project', {}).get('name')+'-sa'
                    #doc['spec']['template']['spec']['volumes'][0]['persistentVolumeClaim']['claimName'] = config_yaml.get('project', {}).get('name')+'-'+config_yaml.get('project', {}).get('notebook', {}).get('name')+'-mc-pvc'
                    for container in doc['spec']['template']['spec']['containers']:
                        #if 'mc' in container['command'][-1]:
                        #    container['command'][-1] = 'mc alias set myminio http://minio:9000 $MINIO_ACCESS_KEY $MINIO_SECRET_KEY && mc mb '+config_yaml.get('project', {}).get('name')+'/'+config_yaml.get('project', {}).get('name')+'-mlpipeline'
                        if container['name'] == 'create-bucket':
                            secret_name = config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('s3CredentialsSecret', {}).get('secretName')
                            for env in container['env']:
                                if env['name'] == 'MINIO_ACCESS_KEY':
                                    env['valueFrom']['secretKeyRef']['name'] = secret_name
                                    env['valueFrom']['secretKeyRef']['key'] = 'accesskey'
                                elif env['name'] == 'MINIO_SECRET_KEY':
                                    env['valueFrom']['secretKeyRef']['name'] = secret_name
                                    env['valueFrom']['secretKeyRef']['key'] = 'secretkey'

            elif kind == 'Notebook':
                small_mig = 'nvidia.com/mig-1g.5gb'
                medium_mig = 'nvidia.com/mig-2g.10gb'
                large_mig = 'nvidia.com/mig-3g.20gb'
                gpu = config_yaml.get('project', {}).get('notebook', {}).get('gpu')
                mig = config_yaml.get('project', {}).get('notebook', {}).get('mig')
                # Assuming each notebook has a single container where updates are necessary
                notebook_container = doc['spec']['template']['spec']['containers'][0]
                notebook_template_spec = doc['spec']['template']['spec']
                notebook_template_spec.update({'affinity': {'nodeAffinity': {}}})
                notebook_scheduler = notebook_template_spec['affinity']
                notebook_template_spec.update({'tolerations':[]})
                notebook_toleration = notebook_template_spec['tolerations']
                if gpu.lower() == 'yes' and mig.lower() == 'yes':
                    tolerate = 'A100'
                    notebook_scheduler['nodeAffinity'] = {'requiredDuringSchedulingIgnoredDuringExecution': {'nodeSelectorTerms': [{'matchExpressions': [{'key': 'nvidia.com/gpu.product', 'operator' : 'In', 'values': ['NVIDIA-A100-SXM4-40GB']}]}]}}
                elif gpu.lower() == 'yes' and mig.lower() != 'yes':
                    tolerate = 'A10'
                    notebook_scheduler['nodeAffinity'] = {'requiredDuringSchedulingIgnoredDuringExecution': {'nodeSelectorTerms': [{'matchExpressions': [{'key': 'nvidia.com/gpu.product', 'operator' : 'In', 'values': ['NVIDIA-A10G']}]}]}}
                else:
                    tolerate = ''
                    # notebook_scheduler['nodeAffinity'] = {'requiredDuringSchedulingIgnoredDuringExecution': {'nodeSelectorTerms': [{'matchExpressions': [{'key': 'node-role.kubernetes.io', 'operator' : 'In', 'values': ['worker']}]}]}}
                notebook_container['image'] = config_yaml.get('project', {}).get('notebook', {}).get('image')
                if notebook_container['env'][0]['name'] == 'NOTEBOOK_ARGS':
                    notebook_container['env'][0]['value'] = "--ServerApp.port=8888 --ServerApp.token='' --ServerApp.password='' --ServerApp.base_url=/notebook/{project_name}/{notebook_name}".format(
                        project_name=os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml.get('project', {}).get('name'),
                        notebook_name=config_yaml.get('project', {}).get('notebook', {}).get('name')
                    )
                if notebook_container['env'][1]['name'] == 'JUPYTER_IMAGE':
                    notebook_container['env'][1]['value'] = config_yaml.get('project', {}).get('notebook', {}).get('image')
                if 'name' in notebook_container['envFrom'][0]['secretRef']:
                    notebook_container['envFrom'][0]['secretRef']['name'] = config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('s3CredentialsSecret', {}).get('secretName')
                notebook_container['resources']['requests'] = {
                    'cpu': config_yaml.get('project', {}).get('notebook', {}).get('cpuRequest'),
                    'memory': config_yaml.get('project', {}).get('notebook', {}).get('memoryRequest')
                }
                notebook_container['resources']['limits'] = {
                    'cpu': config_yaml.get('project', {}).get('notebook', {}).get('cpuLimit'),
                    'memory': config_yaml.get('project', {}).get('notebook', {}).get('memoryLimit')
                }
                #doc['metadata']['namespace'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml.get('project', {}).get('name')
                notebook_metadata = doc['metadata']
                if config_yaml.get('project', {}).get('notebook', {}).get('notebookSize'):
                    size = config_yaml.get('project', {}).get('notebook', {}).get('notebookSize')
                    if tolerate != '':
                        if tolerate == 'A100':
                            notebook_toleration.append({'key': 'nvidia.com/gpu', 'effect': 'NoSchedule', 'value': 'NVIDIA-A100-SHARED'})
                        elif tolerate == 'A10':
                            notebook_toleration.append({'key': 'nvidia-gpu-only', 'effect': 'NoSchedule'})
                        
                    if size == 'Small' and gpu.lower() == 'yes' and mig.lower() == 'yes':
                        notebook_metadata['annotations']['opendatahub.io/recommended-accelerators'] = '["nvidia.com/mig-1g.5gb"]'
                        notebook_container['resources']['limits'][small_mig] = str(1)
                        notebook_container['resources']['requests'][small_mig] = str(1)
                        
                    elif size == 'Medium' and gpu.lower() == 'yes' and mig.lower() == 'yes':
                        notebook_metadata['annotations']['opendatahub.io/recommended-accelerators'] = '["nvidia.com/mig-2g.10gb"]'
                        notebook_container['resources']['limits'][medium_mig] = str(1)
                        notebook_container['resources']['requests'][medium_mig] = str(1)
                        
                    elif size== 'Large' and gpu.lower() == 'yes' and mig.lower() == 'yes':
                        notebook_metadata['annotations']['opendatahub.io/recommended-accelerators'] = '["nvidia.com/mig-3g.20gb"]'
                        notebook_container['resources']['limits'][large_mig] = str(1)
                        notebook_container['resources']['requests'][large_mig] = str(1)
                notebook_metadata['annotations']['openshift.io/description']=config_yaml.get('project', {}).get('notebook', {}).get('description')
                notebook_metadata['annotations']['openshift.io/display-name']=config_yaml.get('project', {}).get('notebook', {}).get('displayName')
                notebook_metadata['labels']['app']=config_yaml.get('project', {}).get('notebook', {}).get('appLabel')
                notebook_metadata['labels']['component']=config_yaml.get('project', {}).get('notebook', {}).get('name')+'-notebook-instance'
                notebook_metadata['labels']['purpose']=config_yaml.get('project', {}).get('notebook', {}).get('description')
                notebook_metadata['name']=config_yaml.get('project', {}).get('notebook', {}).get('name')
                notebook_container['name'] = config_yaml.get('project', {}).get('notebook', {}).get('name')
                notebook_container['livenessProbe']['httpGet']['path'] = '/notebook/'+os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml.get('project', {}).get('name')+'/'+config_yaml.get('project', {}).get('notebook', {}).get('name')+'/api'
                notebook_container['readinessProbe']['httpGet']['path'] = '/notebook/'+os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml.get('project', {}).get('name')+'/'+config_yaml.get('project', {}).get('notebook', {}).get('name')+'/api'
                if notebook_container['volumeMounts'][0]['mountPath'] == '/opt/app-root/src':
                    notebook_container['volumeMounts'][0]['name'] = config_yaml.get('project', {}).get('notebook', {}).get('name')
                doc['spec']['template']['spec']['serviceAccountName'] = config_yaml.get('project', {}).get('notebook', {}).get('name')
                if 'persistentVolumeClaim' in doc['spec']['template']['spec']['volumes'][0].keys():
                    doc['spec']['template']['spec']['volumes'][0]['name'] = config_yaml.get('project', {}).get('notebook', {}).get('name')
                    doc['spec']['template']['spec']['volumes'][0]['persistentVolumeClaim']['claimName'] = config_yaml.get('project', {}).get('name')+'-'+config_yaml.get('project', {}).get('notebook', {}).get('type')+'-'+config_yaml.get('project', {}).get('notebook', {}).get('name')+'-workbench-pvc'

            # Update ConfigMap for artifact storage configuration
            elif doc['kind'] == 'ConfigMap' and 'artifactRepository' in doc['data']:
                project_name = config_yaml.get('project', {}).get('name')
                doc['metadata']['namespace'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+project_name
                object_storage_host = config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('host')
                object_storage_port = config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('port')
                doc['data']['artifactRepository'] = f"""
                    archiveLogs: false
                    s3:
                      endpoint: "https://{object_storage_host}"
                      bucket: "{project_name}"
                      keyFormat: "artifacts/{{{{workflow.name}}}}/{{{{workflow.creationTimestamp.Y}}}}/{{{{workflow.creationTimestamp.m}}}}/{{{{workflow.creationTimestamp.d}}}}/{{{{pod.name}}}}"
                      insecure: true
                      accessKeySecret:
                        name: "ds-pipeline-extobjstor-creds"
                        key: "AWS_ACCESS_KEY_ID"
                      secretKeySecret:
                        name: "ds-pipeline-extobjstor-creds"
                        key: "AWS_SECRET_ACCESS_KEY"
                    """

            # Update ConfigMap for bucket creation
            elif kind == 'ConfigMap' and doc['metadata']['name'].startswith('create-minio-bucket-script'):
                #doc['metadata']['namespace'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml.get('project', {}).get('name')
                project_name = config_yaml.get('project', {}).get('name')
                object_storage_host = config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('host')
                object_storage_port = config_yaml.get('objectStorage', {}).get('externalStorage', {}).get('port')
                doc['data']['create-bucket.sh'] = f"""
                    #!/bin/sh

                    set -e

                    MINIO_SERVER='https://{object_storage_host}'
                    BUCKET_NAME='{project_name}'

                    echo "Creating MinIO bucket: $BUCKET_NAME"

                    curl -X PUT "$MINIO_SERVER/$BUCKET_NAME" \
                      -H "Authorization: Bearer $(curl -u $MINIO_ACCESS_KEY:$MINIO_SECRET_KEY -X POST "$MINIO_SERVER/minio/admin/v3/tenants/")"
                """
            # Update Project configuration
            elif kind == 'Project':
                doc['metadata']['name'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml['project']['name']
                doc['metadata']['annotations']['openshift.io/description'] = "Auto-generated DataScienceProject for User: {}".format(config_yaml['project']['user'])
                doc['metadata']['annotations']['openshift.io/display-name'] = config_yaml['project']['name']
                doc['metadata']['annotations']['openshift.io/requester'] = config_yaml['project']['user']
                doc['metadata']['labels']['opendatahub.io/dashboard'] = "true"
                doc['metadata']['labels']['kubernetes.io/metadata.name'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml['project']['name']
                #doc['metadata']['annotations']['kubectl.kubernetes.io/last-applied-configuration'] = None
            
            # Update S3 Bucket details for Project
            elif kind == 'ObjectBucketClaim':
                doc['metadata']['name'] = config_yaml['project']['name']
                doc['metadata']['annotations']['openshift.io/description'] = "Auto-generated S3 Bucket for User: {}".format(config_yaml['project']['user'])
                doc['metadata']['annotations']['openshift.io/display-name'] = config_yaml['project']['name']
                doc['metadata']['annotations']['openshift.io/requester'] = config_yaml['project']['user']
                doc['metadata']['labels']['opendatahub.io/dashboard'] = "true"
                doc['spec']['bucketName'] = config_yaml['project']['name']
                
            # Update ConfiMap for Viewer UI 
            elif kind == 'ConfigMap' and doc['metadata']['name'].startswith('ds-pipeline-ui-configmap'):
                doc['data']['viewer-pod-template.json'] = '''
                    {{
                        "spec": {{
                            "serviceAccountName": "{}"
                        }}
                    }}
                    '''.format(config_yaml['project']['user'])
                #doc['metadata']['namespace'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml.get('project', {}).get('name')

            # Update ServiceAccount and related RBAC configurations
            elif kind == 'ServiceAccount' and 'metadata' in doc:
                project_name = config_yaml.get('project', {}).get('name')
                if project_name:
                    if 'envoy' in doc['metadata']['name']:
                        doc['metadata']['name'] = f"ds-pipelines-envoy-proxy-tls-dspa"
                    else:
                        doc['metadata']['name'] = f"{project_name}-sa"
                    
                #doc['metadata']['namespace'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+config_yaml.get('project', {}).get('name')
                #doc['imagePullSecrets'][0]['name'] = 'image-deployer-secret'

            elif kind == 'Role':
                project_name = config_yaml.get('project', {}).get('name')
                #doc['metadata']['namespace'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+project_name
                # Assume role rules do not change; they are likely not specified in values.yaml

            elif kind == 'RoleBinding':
                project_name = config_yaml.get('project', {}).get('name')
                #doc['metadata']['namespace'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+project_name
                doc['subjects'][0]['name'] = "{}-sa".format(project_name)
                doc['subjects'][0]['namespace'] = os.path.dirname(os.getcwd()).split('/')[-1].lower()+'-'+project_name
                if 'notebook' in doc['metadata']['name']:
                    doc['subjects'][0]['name'] = config_yaml.get('project', {}).get('notebook', {}).get('name')

    return yaml.dump_all(helm_data, default_flow_style=False, allow_unicode=True)

if __name__ == "__main__":
    # Read Helm output from stdin
    helm_output = sys.stdin.read()
    # Ensure there's input to process
    if not helm_output.strip():
        print("Error: No input received from Helm.", file=sys.stderr)
        sys.exit(1)
    # Path to project specific values, dynamically received
    new_values_path = os.getcwd()+'/config/configmap.yaml'
    #new_values_path = sys.argv[1]
    # Merge and output the modified YAML
    modified_yaml = merge_values(helm_output, new_values_path)
    print(modified_yaml)
