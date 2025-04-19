import { renderPiece } from "./chess_utils";

const ChessSquare = ({ 
    row, 
    col, 
    piece, 
    isSelected, 
    isLegalMove, 
    isCapture, 
    onClick 
}) => {
    const getHighlightClass = () => {
        if (isSelected) {
            return 'border-4 border-yellow-500';
        }
        if (isLegalMove) {
            return isCapture ? 'border-4 border-red-500' : 'border-4 border-green-500';
        }
        return '';
    };

    const isLightSquare = (row + col) % 2 === 0;
    const squareColor = isLightSquare ? 'bg-[#eeeed2]' : 'bg-[#769656]';

    return (
        <div
            className={`w-[75px] h-[75px] ${squareColor} ${getHighlightClass()} transition-colors duration-200 flex justify-center items-center cursor-pointer hover:opacity-90`}
            onClick={() => onClick(row, col)}
        >
            {piece && renderPiece(piece)}
        </div>
    );
};

export default ChessSquare; 