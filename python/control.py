import radial_distribution
import plots_over_time
import plots_analysis
import propensity
import positions
import analysis
import setup

# Check for needed directories at start
setup.setup()


class control(object):
    '''A class for controlling the sequence of scripts run'''

    def analyze(initial_skip):
        '''
        The mean squared displacement is calculated by analysis.
        The propensity for motion is calculated by propensity_for_motion.
        The sum of displacements is calculated by propensity.
        '''

        print('Crunching data')
        analysis.analyze(initial_skip)
        positions.traveled()
        propensity.propensity()

    def plot_system():
        '''
        System aspects such as temperature, pressure, volume, etc are plotted
        against the timestep by plots_over_time.
        '''

        print('Plotting data from systems')
        plots_over_time.plot()

    def plot_analysis(stop, point):
        '''
        The plots for mean squared displacement and propensity for motion are
        generated here. Each run has its own plot as well as an overall plot
        that contains all runs for both mean squred displacement and propensity
        for motion. Radial distribution function plots are also saved.
        '''

        print('Plotting the analysis data')
        plots_analysis.plot(stop)
        radial_distribution.plot(point)

    def clean():
        '''
        This clears all data generated by LAMMPS and python scripts. Do not run
        if any data is needed for future reference.
        '''

        print('Deleting all data')
        setup.clean()
