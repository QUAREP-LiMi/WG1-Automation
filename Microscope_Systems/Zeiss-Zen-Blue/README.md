Copyright 2022 Nasser Darwish Miranda

@author: Nasser Darwish, IST Austria

This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
	
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

Authorship and rights

- The QUAREP-LPM.py macro, together with the original version of the documents and 
configuration files were created By Nasser Darwish <nasser.darwish-miranda@ist.ac.at> 
at IST Austria

- The TLPM.py and TLPM.dll files are provided by Tholabs GmbH <www.thorlabs.com> in the driver 
package for their power meters. The "measurePowers.pyw" script was derived from an example 
file, also distributed by Tholabs GmbH.


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





