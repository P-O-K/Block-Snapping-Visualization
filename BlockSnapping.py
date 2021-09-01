
import pygame; pygame.init( )
import Constants as const
from math import sqrt



class Block( object ):
    """docstring for Block"""

    BLOCK   :pygame.Rect


    def __init__( self ) -> None:
        super( Block, self ).__init__( )
        self.BLOCK = pygame.Rect( 0, 0, const.BLOCK_WIDTH, const.BLOCK_HEIGHT )



    def renderObject( self, displayWindow:pygame.display ) -> None:
        pygame.draw.rect( displayWindow, const.BLOCK_COLOR, self.BLOCK, const.BLOCK_FILL )



    def updatePosition( self ) -> None:
        self.BLOCK.center = pygame.mouse.get_pos( )





class BlockLite( Block ):
    """docstring for BlockLite"""

    BOUNDING_BOX        :pygame.Rect
    SNAPPING_BLOCKS     :dict


    def __init__( self, RECT:pygame.Rect ) -> None:
        super( ).__init__( )

        self.BLOCK.center = RECT.center
        self.BOUNDING_BOX = pygame.Rect( 0, 0, const.BLOCK_WIDTH*const.BLOCK_SCALE_FACTOR, const.BLOCK_HEIGHT*const.BLOCK_SCALE_FACTOR )
        self.BOUNDING_BOX.center = self.BLOCK.center
        self.SNAPPING_BLOCKS = { 'NORTH':   pygame.Rect( self.BLOCK.left,                       self.BLOCK.top -const.BLOCK_HEIGHT, const.BLOCK_WIDTH, const.BLOCK_HEIGHT ),
                                 'SOUTH':   pygame.Rect( self.BLOCK.left,                       self.BLOCK.bottom,                  const.BLOCK_WIDTH, const.BLOCK_HEIGHT ),
                                 'EAST':    pygame.Rect( self.BLOCK.right,                      self.BLOCK.top,                     const.BLOCK_WIDTH, const.BLOCK_HEIGHT ),
                                 'WEST':    pygame.Rect( self.BLOCK.left -const.BLOCK_WIDTH,    self.BLOCK.top,                     const.BLOCK_WIDTH, const.BLOCK_HEIGHT ) }




    def renderBoundingBox( self, displayWindow:pygame.display ) -> None:
        pygame.draw.rect( displayWindow, const.BOUNDING_BOX_COLOR, self.BOUNDING_BOX, const.BLOCK_LINEWIDTH )


    @staticmethod
    def renderSnappingPoint( displayWindow:pygame.display,  sPoint:pygame.Rect ) -> None:
        pygame.draw.rect( displayWindow, const.SNAPPING_POINT_COLOR, sPoint, const.BLOCK_FILL )



    def renderAllSnappingPoints( self, displayWindow:pygame.display ) -> None:
        for _, object in self.SNAPPING_BLOCKS.items( ):
            pygame.draw.rect( displayWindow, const.SNAPPING_POINT_COLOR, object, const.BLOCK_LINEWIDTH )





class BlockSnapping( object ):
    """docstring for BlockSnapping"""

    MAIN_DISPLAY = pygame.display.set_mode( ( const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT ) )
    pygame.display.set_caption( const.DISPLAY_WINDOW_NAME )
    CLOCK = pygame.time.Clock( )

    ghostBlock          :Block
    blockLiteArray      :list
    historyArray        :list


    def __init__( self ) -> None:
        super( BlockSnapping, self ).__init__( )
        self.ghostBlock         = Block( )
        self.blockLiteArray     = list( )
        self.historyArray       = list( )
        self.mainLoop( )



    def checkNearestNeighbour( self ) -> Block:
        neighbour, neighbourDistance = False, max( const.BLOCK_WIDTH, const.BLOCK_HEIGHT ) *const.BLOCK_SCALE_FACTOR

        for object in self.blockLiteArray:
            if object.BOUNDING_BOX.colliderect( self.ghostBlock.BLOCK ):

                sampleDistance = self.euclideanDistance( self.ghostBlock.BLOCK.center, object.BLOCK.center )
                if sampleDistance < neighbourDistance:
                    neighbour, neighbourDistance = object, sampleDistance

        return neighbour



    def checkSnappingPoints( self, neighbour:Block ) -> pygame.Rect:
        snapDistance = max( const.BLOCK_WIDTH, const.BLOCK_HEIGHT ) *const.BLOCK_SCALE_FACTOR

        for _, object in neighbour.SNAPPING_BLOCKS.items( ):
                sampleDistance = self.euclideanDistance( self.ghostBlock.BLOCK.center, object.center )

                if sampleDistance < snapDistance:
                    snapPoint, snapDistance = object, sampleDistance

        return snapPoint



    def addSnapPointBlock( self, snapPoint:pygame.Rect ) -> None:
        for object in self.blockLiteArray:
                if snapPoint.colliderect( object.BLOCK ): snapPoint = None; break
        if snapPoint: self.blockLiteArray.append( BlockLite( snapPoint ) )



    def removeBlock( self ) -> None:
        for E, object in enumerate( self.blockLiteArray ):
            if object.BLOCK.collidepoint( pygame.mouse.get_pos( ) ):
                self.blockLiteArray.pop( E )



    @staticmethod
    def euclideanDistance( one:tuple, two:tuple ) -> int:
        return sqrt( sum( [ ( a -b )**2 for a, b in zip( one, two ) ] ) )



    @staticmethod
    def clearDisplay( displayWindow:pygame.display ) -> None:
        displayWindow.fill( const.BACKGROUND_COLOR )



    def renderDisplay( self, neighbour:Block, sPoint:pygame.Rect ) -> None:
        for object in self.blockLiteArray:
            object.renderObject( displayWindow=self.MAIN_DISPLAY )

        if neighbour: neighbour.renderBoundingBox( displayWindow=self.MAIN_DISPLAY )
        if sPoint: neighbour.renderSnappingPoint( displayWindow=self.MAIN_DISPLAY, sPoint=sPoint )
        if sPoint: neighbour.renderAllSnappingPoints( displayWindow=self.MAIN_DISPLAY )

        self.ghostBlock.renderObject( displayWindow=self.MAIN_DISPLAY )



    def updateDisplay( self ) -> None:
        self.CLOCK.tick( const.FRAMERATE )
        pygame.display.update( )



    def eventManager( self, sPoint:pygame.Rect ) -> bool:
        for event in pygame.event.get( ):
            if event.type == pygame.QUIT: return True

            if event.type == pygame.MOUSEBUTTONDOWN:

                if( event.button == 1 ):                                                        # LEFT MOUSE BUTTON
                    self.addSnapPointBlock( sPoint if sPoint else self.ghostBlock.BLOCK )
                    self.historyArray = list( )

                if( event.button == 2 ):                                                        # MIDDLE MOUSE BUTTON
                    self.removeBlock( )

                if( event.button == 3 ):                                                        # RIGHT MOUSE BUTTON
                    self.addSnapPointBlock( self.ghostBlock.BLOCK )
                    self.historyArray = list( )

                if ( event.button == 4 ) & ( len( self.historyArray ) >0 ):                     # MOUSE WHEEL UP
                    self.blockLiteArray.append( self.historyArray.pop( ) )

                if ( event.button == 5 ) & ( len( self.blockLiteArray ) >0 ):                   # MOUSE WHEEL DOWN
                    self.historyArray.append( self.blockLiteArray.pop( ) )

        return False



    def mainLoop( self ) -> None:
        ExitStatus = False
        while not ExitStatus:
            self.clearDisplay( self.MAIN_DISPLAY )
            self.ghostBlock.updatePosition( )

            neighbour = self.checkNearestNeighbour( )
            snapPoint = self.checkSnappingPoints( neighbour ) if neighbour else None

            ExitStatus = self.eventManager( sPoint=snapPoint )

            self.renderDisplay( neighbour=neighbour, sPoint=snapPoint )
            self.updateDisplay( )

        pygame.quit( )




if __name__ == '__main__':
    BlockSnapping( )
    raise SystemExit

