'''
Created on 2021-08-07

@author: wf
'''
from corpus.quality.rating import EntityRating

class EventRating(EntityRating):
    '''
    a rating for an event
    '''
    
    def __init__(self,event):
        super().__init__(self,event,event.eventId,event.source,"Event")
        
class EventSeriesRating(EntityRating):
    '''
    a rating for an event
    '''
    
    def __init__(self,eventSeries):
        super().__init__(self,eventSeries,eventSeries.seriesId,eventSeries.source,"EventSeries")
        