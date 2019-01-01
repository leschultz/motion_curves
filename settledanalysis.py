from PyQt5 import QtGui  # Added to be able to import ovito

from matplotlib import pyplot as pl
from infoparser import parameters
from outimport import readdata
from settleddataclass import settled

import numpy as np
import os


def run(param, savepath):
    for item in param:

        path = item.replace('uwtraj.lammpstrj', '')
        outfile = path+'test.out'
        printname = 'Settling Methods for Run: '+outfile

        folder = '/'+path.split('/')[-2]

        print('-'*len(printname))
        print(printname)
        print('-'*len(printname))

        n = param[item]['iterations']
        increment = param[item]['increment']
        deltatemp = param[item]['deltatemp']
        starttemp = param[item]['tempstart']
        timestep = param[item]['timestep']
        dumprate = param[item]['dumprate']

        hold2 = param[item]['hold2']
        hold3 = param[item]['hold3']

        df = readdata(outfile)

        time = [timestep*i for i in df['Step']]
        df['time'] = time

        for iteration in list(range(0, n)):

            expectedtemp = starttemp-iteration*deltatemp

            print(
                  'Temperature step: ' +
                  str(expectedtemp) +
                  ' [K]'
                  )

            savename = (
                        item.split('/')[-2] +
                        '_' +
                        str(starttemp-iteration*deltatemp).split('.')[0] +
                        'K'
                        )

            hold1 = param[item]['hold1']
            hold1 += iteration*increment

            points = [hold1, hold1+hold2, hold1+hold2+hold3]

            dataindexes = df['Step'].between(points[1], points[2])

            time = list(df['time'][dataindexes])
            temp = list(df['Temp'][dataindexes])

            setindexes = settled(time, temp)
            index = setindexes.binsize()
            binnedtime, binnedtemp = setindexes.batch()

            setindexes.binslopes()

            binnedslopes, slopebin = setindexes.slopetest()
            pvals, pbin, alpha = setindexes.ptestblock()

            fitvals = setindexes.ptestfit(expectedtemp)

            slopeerr = fitvals[0]
            averages = fitvals[1]
            slopeerrbin = fitvals[2]
            start = fitvals[3]
            slopestart = fitvals[4]

            indexes = setindexes.finddatastart()

            settledindex = []
            for key in indexes:
                if isinstance(indexes[key], int):
                    settledindex.append(indexes[key])

            try:
                settledindex = max(settledindex)
            except Exception:
                settledindex = len(time)-1

            fig, ax = pl.subplots()

            binnumber = list(range(1, len(binnedslopes)+1))
            averagetemps = [np.mean(i) for i in binnedtemp]

            ax.plot(
                    binnumber,
                    binnedslopes,
                    label='Input Block Length (b='+str(index)+')',
                    marker='.'
                    )

            try:
                ax.plot(
                        binnumber[slopebin],
                        binnedslopes[slopebin],
                        label='Method: Slope Change',
                        marker='*',
                        markersize=12,
                        linestyle='none',
                        color='g'
                        )

            except Exception:
                ax.plot(
                        binnumber[-1],
                        binnedslopes[-1],
                        label='Method: Slope Change Not Settled',
                        marker='*',
                        markersize=12,
                        linestyle='none',
                        color='g'
                        )

            ax.set_xlabel('Bin')
            ax.set_ylabel('Slope [K/ps]')
            ax.grid()
            ax.legend(loc='best')
            fig.tight_layout()
            fig.savefig(
                        savepath +
                        folder +
                        '/images/settling/methods/slopemethod_' +
                        savename
                        )

            fig, ax = pl.subplots()

            ax.plot(
                    binnumber,
                    pvals,
                    label='Input Block Length (b='+str(index)+')',
                    marker='.'
                    )

            try:
                ax.plot(
                        binnumber[pbin],
                        pvals[pbin],
                        label='Method: p-value',
                        marker='x',
                        markersize=12,
                        linestyle='none',
                        color='r'
                        )

            except Exception:
                ax.plot(
                        binnumber[0],
                        pvals[0],
                        label='Method: p-value Completely Settled',
                        marker='x',
                        markersize=12,
                        linestyle='none',
                        color='r'
                        )

            ax.set_xlabel('Bin')
            ax.set_ylabel('p-value (alpha='+str(alpha)+')')
            ax.grid()
            ax.legend(loc='best')
            fig.tight_layout()
            fig.savefig(
                        savepath+folder +
                        '/images/settling/methods/pmethod_' +
                        savename
                        )

            fig, ax = pl.subplots()

            ax.plot(
                    slopeerr,
                    label='Input Block Length (b='+str(index)+')',
                    marker='.',
                    color='r'
                    )

            ax.axvline(
                       x=slopestart,
                       color='b',
                       linestyle='--',
                       label='Method: Settled Slope'
                       )


            ax.set_xlabel('Data point [-]')
            ax.set_ylabel(
                          'Linear Fit Slope [K/ps] Starting from End'
                          )
            ax.grid()
            ax.legend(loc='best')
            fig.tight_layout()
            fig.savefig(
                        savepath +
                        folder +
                        '/images/settling/methods/endslopes_' +
                        savename
                        )

            fig, ax = pl.subplots()
            ax.plot(
                    averages,
                    label='Input Block Length (b='+str(index)+')',
                    marker='.',
                    color='r'
                    )

            ax.axvline(
                       x=start,
                       color='b',
                       linestyle='--',
                       label='Method: Settled Average'
                       )


            ax.set_xlabel('Data point [-]')
            ax.set_ylabel(
                          'Average Temperature [K] Starting from End'
                          )
            ax.grid()
            ax.legend(loc='best')
            fig.tight_layout()
            fig.savefig(
                        savepath +
                        folder +
                        '/images/settling/methods/averages_' +
                        savename
                        )

            fig, ax = pl.subplots()
            ax.plot(
                    time,
                    temp,
                    marker='.',
                    color='r',
                    linestyle='none'
                    )

            try:
                ax.axvline(
                           x=time[slopeerrbin],
                           color='b',
                           linestyle='--',
                           label='Method: Overall Fit'
                           )

            except Exception:
                ax.axvline(
                           x=time[-1],
                           color='b',
                           linestyle='--',
                           label='Method: Overall Fit not Applicable'
                           )

            ax.set_xlabel('Time [ps]')
            ax.set_ylabel(
                          'Temperature [K]'
                          )
            ax.grid()
            ax.legend(loc='best')
            fig.tight_layout()
            fig.savefig(
                        savepath +
                        folder +
                        '/images/settling/methods/fiterror_' +
                        savename
                        )

            fig, ax = pl.subplots()
            ax.plot(
                    time,
                    temp,
                    linestyle='none',
                    color='r',
                    marker='.',
                    label='Data'
                    )

            ax.axvline(
                       x=time[settledindex],
                       color='b',
                       linestyle='--',
                       label='Settled Start'
                       )

            mean = np.mean(temp[settledindex:])
            ax.axhline(
                       y=mean,
                       color='k',
                       label='Settled Mean='+str(mean)[:5]+' [K]'
                       )

            ax.set_xlabel('Time [ps]')
            ax.set_ylabel('Temperature [K]')
            ax.grid()
            ax.legend(loc='best')
            fig.tight_layout()
            fig.savefig(savepath+folder+'/images/settling/data/data_'+savename)
            pl.close('all')
