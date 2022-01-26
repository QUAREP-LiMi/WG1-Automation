Copyright 2022 Nasser Darwish Miranda

@author: Nasser Darwish, IST Austria

This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version (TO BE DISCUSSED AT WG1 MEETING)

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
	
This program allows automatic power measurements for: 
- Nikon Eclipse Ti2 CSU-W1 Spinning Disk (NIS Elements Ver. 5.x) + Omicron LightHUB Ultra + Thorlabs PM100USB (Optical Power Monitor Ver. 3.1) 


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


Authorship and rights

- The lpm_W1_LongTerm.mac and lpm_W1_ShortTerm.mac macros, together with the original version of these
 documents were created By Nasser Darwish <nasser.darwish-miranda@ist.ac.at> at IST Austria

- The TLPM.py and TLPM.dll files are provided by Tholabs GmbH <www.thorlabs.com> in the driver 
package for their power meters. The "measurePowers.pyw" script was derived from an example file, 
also distributed by Tholabs GmbH.

All rights for the files created by other authors belong to them. Please review their
license terms and follow their instructions to get the up to date versions.

Disclaimer (TO BE DISCUSSED AT THE WG1 USER GROUP MEETING)

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
IN THE SOFTWARE.





https://user-images.githubusercontent.com/98343796/151212163-6a710b9e-d571-48d3-8966-d3442abd1577.mp4





