tmp = 'asfd'

class Redpages:

    def boo(self):
        self.response.write("""\
This <b>is</b> a <r:eval>tmp</r:eval> response!!
      <r:for item="i" list="[0, 1, 2]">
        <r:if test="i==0">
          More
          <r:elseif test="i==1">
            Not sure
          </r:elseif>
          <r:else>
            Less
          </r:else>
        </r:if>
      </r:for>
""")      

    def handle(self, request, response):
        self.request = request
        self.response = response
        self.boo()

rp = Redpages()

def handle_request(request, response):
    if request.get_path_info()=='/':
        rp.handle(request, response)
    else:
        response.write("boo")


