from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from shapely.geometry import LineString, Point, Polygon, box as sbox
from matplotlib.collections import LineCollection
from cartopy.util import add_cyclic_point
from scipy.ndimage import gaussian_filter
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from itertools import product
import cartopy.crs as ccrs
import geopandas as gpd
from glob import glob
import pandas as pd
import xarray as xr
import numpy as np
import warnings


def lon360to180(lon):
    return (lon + 180.0) % 360.0 - 180.0

def lon180to360(lon):
    return lon % 360.0

def wrap_lon_360(lons):
    lons_unwrapped = [lons[0]]
    for lon in lons[1:]:
        if lon < lons_unwrapped[-1] - 180:
            lon += 360
        elif lon > lons_unwrapped[-1] + 180:
            lon -= 360
        lons_unwrapped.append(lon)
    return lons_unwrapped

def sanitize_lonlist(lons):
    new_list = []
    oldval = 0
    threshold = 30  # degrees to detect jumps
    for ix, ea in enumerate(lons):
        diff = oldval - ea
        if ix > 0 and diff > threshold:
            ea = ea + 360  # fix backward jump when crossing the dateline
        elif ix > 0 and diff < -threshold:
            ea = ea - 360  # fix forward jump when crossing the dateline
        oldval = ea
        new_list.append(ea)
    return new_list

def coords_to_track(dfl, track_color):
    x_raw = dfl['lon'].to_numpy(dtype=float)
    x = np.array(sanitize_lonlist(x_raw))
    y = dfl['lat'].to_numpy(dtype=float)
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, color=track_color, alpha=0.5,
                        transform=ccrs.PlateCarree())
    return lc

def plot_track(df, color='',title=''):
    mapcrs = ccrs.PlateCarree(central_longitude=180)  # center on Pacific
    fig = plt.figure(figsize=(7, 4),layout="constrained",facecolor='white', dpi=75)
    ax1 = fig.add_subplot(111,projection=mapcrs)
    xticks = np.arange(-180, 181, 40)
    yticks = np.arange(-70, 71, 20)
    ax1.set_xticks(xticks, crs=ccrs.PlateCarree())
    ax1.set_yticks(yticks, crs=ccrs.PlateCarree())
    ax1.xaxis.set_major_formatter(LongitudeFormatter(zero_direction_label=True))
    ax1.yaxis.set_major_formatter(LatitudeFormatter())
    ax1.add_feature(cfeature.COASTLINE.with_scale('50m'),edgecolor='k',lw=1.25)
    ax1.add_feature(cfeature.OCEAN.with_scale('50m'),facecolor='none')
    ax1.add_feature(cfeature.LAND.with_scale('50m'), facecolor='antiquewhite')
    ax1.set_extent([-180, 180, -80, 80], crs=ccrs.PlateCarree())
    for sid, group in df.groupby('track_id'):
        group = group.copy()
        group['lon'] = group['lon'] % 360  # Ensure all longitudes in 0–360
        trc = coords_to_track(group, color)
        trc.set_linewidth(1)
        ax1.add_collection(trc)
    ax1.set_title(title,fontsize=14, pad=5)
    ax1.set_xlabel(''); ax1.set_ylabel('')
    plt.show()

    return fig

def createGrid(xmin, xmax, ymin, ymax, wide, length):
    cols = list(np.arange(xmin, xmax + wide, wide))
    rows = list(np.arange(ymin, ymax + length, length))
    polygons = []
    for x, y in product(cols[:-1], rows[:-1]):
        polygons.append(
            Polygon([(x, y), (x + wide, y),
                     (x + wide, y + length),
                     (x, y + length)]))
    gridid = np.arange(len(polygons))
    grid = gpd.GeoDataFrame({'gridid': gridid,
                             'geometry': polygons})
    return grid

def addGeometry(trackdf, storm_id_field, lonname, latname):
    tracks = []
    for k, t in trackdf.groupby(storm_id_field):
        lons = t[lonname].values
        lats = t[latname].values
        lons_unwrapped = wrap_lon_360(lons)
        segments = []
        for n in range(len(t) - 1):
            segment = LineString([
                (lons_unwrapped[n], lats[n]),
                (lons_unwrapped[n+1], lats[n+1])
            ])
            segments.append(segment)
        gdf = gpd.GeoDataFrame(t.iloc[:-1].copy())
        gdf["geometry"] = segments
        gdf = gdf.set_geometry("geometry")
        tracks.append(gdf)
    outgdf = pd.concat(tracks, ignore_index=True)
    return outgdf

def gridDensity(tracks, grid, grid_id_field, storm_id_field):
    dfjoin = gpd.sjoin(grid, tracks, how='inner')
    aggregation_functions = {storm_id_field: 'nunique'}
    df2 = dfjoin.groupby(grid_id_field).agg(aggregation_functions)
    dfcount = grid.merge(df2, how='left', left_on=grid_id_field, right_index=True)
    dfcount[storm_id_field] = dfcount[storm_id_field].fillna(0)
    dfcount.rename(columns = {storm_id_field:'storm_count'}, inplace = True)
    dfcount['storm_count'] = dfcount['storm_count'].fillna(0)
    return dfcount

def calcu_track_den(min_lon, max_lon, min_lat, max_lat, delta,
                    df_track, storm_id_field, grid_id_field,
                    lonname, latname):
    minlon =   min_lon
    maxlon =   max_lon
    minlat =   min_lat
    maxlat =   max_lat
    dx = delta
    dy = delta
    lon = np.arange(minlon, maxlon, dx)
    lat = np.arange(minlat, maxlat, dy)
    dfgrid = createGrid(minlon, maxlon, minlat, maxlat, dx, dy)
    dims = (int((maxlon - minlon)/dx), int((maxlat-minlat)/dy))
    dfstorm = addGeometry(df_track, storm_id_field, lonname, latname)
    dfcount = gridDensity(dfstorm, dfgrid, grid_id_field, storm_id_field)
    tcarray = dfcount['storm_count'].values.reshape(dims)
    dc = xr.DataArray(tcarray,coords=[lon, lat], dims=[lonname,latname])
    ds = xr.Dataset({'number': dc})
    
    return ds

def plot_den(dataArray, minlon, maxlon, minlat, maxlat, count_range, sigma, mycmap, title):
    mapcrs = ccrs.PlateCarree(central_longitude=180)
    datacrs = ccrs.PlateCarree()
    fig = plt.figure(figsize=(7, 4), layout="constrained", facecolor='white', dpi=75)
    ax1 = fig.add_subplot(111, projection=mapcrs)
    xticks = np.arange(-180, 181, 40)
    yticks = np.arange(-90+20,   91-20, 20)
    ax1.set_xticks(xticks, crs=ccrs.PlateCarree())
    ax1.set_yticks(yticks, crs=ccrs.PlateCarree())
    ax1.set_extent([minlon, maxlon, minlat, maxlat], ccrs.PlateCarree())
    ax1.xaxis.set_major_formatter(LongitudeFormatter(zero_direction_label=True))
    ax1.yaxis.set_major_formatter(LatitudeFormatter())
    ax1.add_feature(cfeature.COASTLINE.with_scale('50m'),edgecolor='k',lw=1.25)
    ax1.add_feature(cfeature.OCEAN.with_scale('50m'),facecolor='none')
    lon = dataArray.lon.values; lat = dataArray.lat.values
    cdata, clon = add_cyclic_point(dataArray.T, lon)
    cdata_filter = gaussian_filter(cdata, sigma=sigma)
    cf = ax1.contourf(clon, lat, cdata_filter,transform=datacrs,
                      levels=count_range,cmap=mycmap,
                      extend='max')
    cb = plt.colorbar(cf,orientation='horizontal',ticks=count_range,
                     pad=0.04, aspect=40)
    ax1.set_title(title,fontsize=14, pad=5)
    ax1.set_xlabel(''); ax1.set_ylabel('')
    plt.show()

    return fig
