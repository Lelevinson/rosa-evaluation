from importlib.metadata import version
def main():
 if version('arize-phoenix')!='20.23.0':raise RuntimeError('Revalidate HTTP-only shim before changing Phoenix version.')
 from phoenix.server import app
 from phoenix.server.grpc_server import GrpcServer
 class HttpOnlyGrpcServer(GrpcServer):
  def __init__(self,*args,**kwargs):
   kwargs['disabled']=True
   super().__init__(*args,**kwargs)
 app.GrpcServer=HttpOnlyGrpcServer
 from phoenix.server.main import main as serve
 serve()
if __name__=='__main__':main()
