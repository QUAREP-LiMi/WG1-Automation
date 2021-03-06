# Introduction
This program was tested successfully in a specific microscope. We provide it in the hope that it 
is helpful, but we cannot provide support or warranty of any kind. Differences between similar 
microscopes (filters, light paths, etc.) are to be expected and the usually minor adaptations 
needed from one to another require the understanding of the code. Despite unlikely, damage to 
the equipment caused by wrong edits or by unforeseen circumstances is still possible. While 
unlikely, damage to the equipment caused by wrong edits or by unforeseen circumstances is still 
possible. Proceed at your own risk, following the local safety regulations and  by by ensuring 
complete understanding of the programs prior to their execution. In particular, for testing 
purposes we strongly advise to employ low laser power settings and reduced number of loops.

# Installation
This program allows automatic power measurements for: 
- Nikon Eclipse Ti2 CSU-W1 Spinning Disk (tested with NIS Elements Ver. 5.30) + Omicron LightHUB Ultra + Thorlabs PM100USB (Optical Power Monitor Ver. 3.1) 

The underlying hierarchy is: 
- Nikon macro -> measurePowers.pyw -> TLPM.py -> TLPM_64.dll

The Nikon macro runs under NIS Elements. To make it available:

	Copy the .mac file into:
	C:\Program Files\NIS-Elements\Macros	

The Nikon macro connects to a python interpreter (miniconda suggested) and invokes the 
measurePowersThorlabs.pyw script. Finally, the TLPM files bring the low level access to the 
power meter device.

Currently, the configurations cannot be loaded from separate files and the .mac script 
still has to be edited per system. 

# License
The automation script is covered by the 3-Clause BSD license. You can freely use, modify, 
and share it. Only mentioning the origianl authors in a modified version requires prior 
consent.

The additional software necessary is provided and licensed by the corresponding vendors.
To make use of it please review and agree their terms.

# Disclaimer
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





https://user-images.githubusercontent.com/98343796/151212163-6a710b9e-d571-48d3-8966-d3442abd1577.mp4





