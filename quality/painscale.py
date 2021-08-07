'''
Created on 2021-04-16

@author: wf
'''

class PainScale(object):
    '''
    painscale handling
    '''

    @staticmethod
    def lookupPainImage(rating: int,size=64,asImageTag=True):
        '''
        Returns html image tag to the corresponding pain rating
       
        Args:
            rating(int): the pain rating
        '''
        painImages = {
                      0: f"https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Pain_0_png_rendered.png/{size}px-Pain_0_png_rendered.png", 
                      1: f"https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Pain_1_png_rendered.png/{size}px-Pain_1_png_rendered.png",
                      2: f"https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Pain_2_png_rendered.png/{size}px-Pain_2_png_rendered.png",
                      3: f"https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Pain_2_png_rendered.png/{size}px-Pain_2_png_rendered.png",
                      4: f"https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Pain_3_png_rendered.png/{size}px-Pain_3_png_rendered.png",
                      5: f"https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Pain_5_png_rendered.png/{size}px-Pain_5_png_rendered.png",
                      6: f"https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Pain_6_png_rendered.png/{size}px-Pain_6_png_rendered.png",
                      7: f"https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Pain_7_png_rendered.png/{size}px-Pain_7_png_rendered.png",
                      8: f"https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Pain_8_png_rendered.png/{size}px-Pain_8_png_rendered.png",
                      9: f"https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Pain_9_png_rendered.png/{size}px-Pain_9_png_rendered.png",
                     10: f"https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Pain_10_png_rendered.png/{size}px-Pain_10_png_rendered.png"
                      }
        if rating >= 0 and rating <= 10:
            src=painImages[rating]
            if asImageTag:
                return f'<img alt="{rating}" src="{src}" width="{size}" height="{size}"/>'
            else:
                return src
        else:
            return ""