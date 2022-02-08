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


Authorship and rights

- The LPM-loop.mac macro, together with the original version of these documents was created by 
Nasser Darwish <nasser.darwish-miranda@ist.ac.at> at IST Austria.

 - The TLPM.py and TLPM.dll files are provided by Tholabs GmbH <www.thorlabs.com> in the driver package for 
 their power meters. The "measurePowers.pyw" script was derived from an example file, also distributed by 
 Tholabs GmbH.

All rights for the files created by other authors belong to them. Please review their
license terms and follow their instructions to get the up to date versions.

Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
IN THE SOFTWARE.



https://user-images.githubusercontent.com/98343796/151208904-a98e733d-c1d9-4329-9357-12c91b90e7d5.mp4


