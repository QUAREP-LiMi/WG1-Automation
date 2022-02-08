This program allows automatic power measurements for Nikon microscopes running NIS Elements (<b> which version?</b> )

This software follows this hierarchy: Nikon macro -> measurePowers.pyw -> TLPM.py -> TLPM_64.dll


The Nikon macro runs under NIS Elements. To make it available:

	Copy the .mac file into:
	C:\Program Files\NIS-Elements\Macros	

The Nikon macro connects to a python interpreter (miniconda suggested) and invokes the 
measurePowers.pyw script. Finally, the TLPM files bring the low level access to the 
power meter device.

Currently the configurations cannot be loaded from separate files and the .mac script 
still has to be edited per system. 

...

The automation script is covered by the 3-Clause BSD license. You can freely use, modify, 
and share it. Only mentioning the origianl authors in a modified version requires prior 
consent.

The additional software necessary is provided and licensed by the corresponding vendors.
To make use of it in other ways keep please review their terms.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT 
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY 
OF SUCH DAMAGE.


https://user-images.githubusercontent.com/98343796/151208904-a98e733d-c1d9-4329-9357-12c91b90e7d5.mp4


