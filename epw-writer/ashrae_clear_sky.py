import math

global_solar_constant = 1367.0
SunIsUpValue = 0.001

# A function to convert sky cover to beam_rad, dif_rad
def ashrae_clear_sky(cloud_cover_perc, cos_zenith, A, B, C, AVSC):
    if cos_zenith >= SunIsUpValue:
        sky_clearness = 1 - cloud_cover_perc
        exponent = B / cos_zenith
        if (exponent > 700.0):
            total_horizontal = 0.0
        else:
            total_horizontal = sky_clearness * A * (C + cos_zenith) * math.exp(-B / cos_zenith)

        HO = global_solar_constant * AVSC * cos_zenith
        KT = total_horizontal / HO
        KT = min(KT, 0.75)
        dif_rad = total_horizontal * (1.0045 + KT * (0.04349 + KT * (-3.5227 + 2.6313 * KT)))
        if (sky_clearness > 0.70):
            dif_rad = total_horizontal * C / (C + cos_zenith)
        beam_rad = (total_horizontal - dif_rad) / cos_zenith
        dif_rad = max(0.0, dif_rad)
        beam_rad = max(0.0, beam_rad)
    else:
        beam_rad = 0.0
        dif_rad = 0.0
    return (str(round(beam_rad, 3)), str(round(dif_rad, 3)))