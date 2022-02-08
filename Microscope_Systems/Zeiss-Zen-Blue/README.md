This program allows automatic power measurements for Zeiss microscopes running Zen Blue

This software follows this hierarchy: Zen macro -> measurePowers.pyw -> TLPM.py -> TLPM_64.dll


The "Zen macro" runs under Zen Blue. To make it available:

	Copy the python file called QUAREP-LPM.py into:
	C:\Users\desiredUsser\Documents\Carl Zeiss\ZEN\Documents\Macros
	If desiredUsser is "all users" the macro will be available for all windows users

The Zen macro connects to a python interpreter (miniconda suggested) and invokes the 
measurePowers.pyw script. Finally, the TLPM files bring the low level access to the 
power meter device.

The Zen software needs to load configuration files to setup the light sources. In this
way the macro can be adapted to different microscopes, as long as the configuration files
are created at the same system. These files should be stored in the "Configs" folder.

The measurementConfig.csv file contains the instructions needed to relove all the 
dependencies. This can be customized if the files are saved in different locations.

...

This program was tested successfully a specific microscope. We provide it in the hope that it 
is helpful, but we cannot provide support or warranty of any kind. Differences between similar 
microscopes (filters, light paths, etc.) are to be expected and the usually minor adaptations 
needed from one to another require the understanding of the code. Despite unlikely, damage to 
the equipment caused by wrong edits or by unforeseen circumstances is still possible. Proceed 
at your own risk, following the applicable safety regulations and keeping sure to understand 
the programs before trying them. In particular, for testing purposes we strongly advice to 
check the code for setting very low illumination powers, limiting the number of loops and 
shortening times while the light sources are on.

The automation script is covered by the 3-Clause BSD license. You can freely use, modify, 
and share it. Only mentioning the origianl authors in a modified version requires prior 
consent.

The additional software necessary is provided and licensed by the corresponding vendors.
To make use of it please review and agree their terms.

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



https://user-images.githubusercontent.com/98343796/151044552-8c5d6b1f-7187-45c1-bb45-604c2456042b.mp4




