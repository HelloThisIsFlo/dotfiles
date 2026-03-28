// Copied fro 'uniform-columns'
function layout() {
  // Small: ~1650 - Large: ~5090 - It changes with the margin
  const LARGE_SCREEN_WIDTH_TRHESHOLD = 2500;

  /*
  =======================
      Layout Behavior
  =======================


  Small Screen (< LARGE_SCREEN_WIDTH_TRHESHOLD px)
  =======================
  This behaves as a tall layout (see 'extends' below)



  Large Screen (> LARGE_SCREEN_WIDTH_TRHESHOLD px)
  =======================

  Panes
  -----
  * The left pane contains a window that will always remain there (e.g. OmniFocus task manager)
    - TODO: Later I could rename this "pinned windows" and allow increasing the count via custom commands
  * The main pane contains the main windows (e.g. VSCode, Chrome, etc.)
    - The number of windows in the main pane can be increased/decreased via custom commands
  * The secondary pane contains all the remaining windows, they compress to fit the pane

  Increasing/Decreasing the main pane count
  -----------------------------------------
  * When increasing the count, the 1st secondary window will be added to the right of the main pane
  * When decreasing the count, the last main window will become the 1st secondary window

  Adding/Removing a window
  ------------------------
  * When adding a window it will take the spot of the main window
  * When removing a window, the 1st secondary window will become the main window

  Cycling windows
  ---------------
  *Navigating focus respects the clockwise/counterclockwise order
    - This is because pinned windows are at the end of the list, so the next after the last pinned window is the 1st main window
  *Swapping windows clockwise/counterclockwise will also respect the clockwise/counterclockwise order
    - For the same reason


  TODO: FIX BUG => Actually, since I implemented the 'Adding/Removing a window' behavior, the cycling is broken. At the moment I can't change the order of the windows in the main program, so I could instead re-implement the cycling via 2 custom commands.
  That means I won't have enough commands to implement cycling AND swapping, so I'll have to choose one of them.
  That being said, if I really NEED more commands I can always implement a "layer" system, like on the keyboard.
  */


  /*************************/
  /***      Config       ***/
  /*************************/
  // const SINGLE_WINDOW_MARGIN_X = 140;
  // const SINGLE_WINDOW_MARGIN_Y = 30;
  const SINGLE_WINDOW_MARGIN_X = 346;
  const SINGLE_WINDOW_MARGIN_Y = -4;
  const SINGLE_WINDOW_OFFSET_Y = -11;



  const getFrameAssignmentsForLargeScreen = (state, windows, screenFrame) => {
    console.log("Large screen");

    const paneCounts =
      windows.length <= state.mainPaneCount
        ? {
            left: 0,
            main: state.mainPaneCount,
            secondary: 0,
          }
        : {
            left: 1,
            main: state.mainPaneCount,
            secondary: windows.length - state.mainPaneCount - 1,
          };

    const basePaneWidth = Math.round(screenFrame.width / 6);

    const leftPaneWidth = basePaneWidth;
    const mainPaneWidth = basePaneWidth * 3;
    const secondaryPaneWidth =
      screenFrame.width - mainPaneWidth - leftPaneWidth;

    const mainPaneWindowWidth = Math.round(mainPaneWidth / paneCounts.main);
    const secondaryPaneWindowWidth =
      paneCounts.secondary !== 0
        ? Math.round(secondaryPaneWidth / paneCounts.secondary)
        : 0;

    return windows.reduce((frames, window, index) => {
      const computeFrame = () => {
        const isLeftWindow =
          paneCounts.left == 1 && index == windows.length - 1;
        if (isLeftWindow) {
          return {
            x: screenFrame.x,
            y: screenFrame.y,
            width: leftPaneWidth,
            height: screenFrame.height,
          };
        }

        const isMainWindow = index < paneCounts.main;
        if (isMainWindow) {
          const baseOffset = screenFrame.x + leftPaneWidth;
          return {
            x: baseOffset + mainPaneWindowWidth * index,
            y: screenFrame.y,
            width: mainPaneWindowWidth,
            height: screenFrame.height,
          };
        }

        const secondaryIndex = index - paneCounts.main;
        const baseOffset = screenFrame.x + leftPaneWidth + mainPaneWidth;
        return {
          x: baseOffset + secondaryPaneWindowWidth * secondaryIndex,
          y: screenFrame.y,
          width: secondaryPaneWindowWidth,
          height: screenFrame.height,
        };
      };

      return { ...frames, [window.id]: computeFrame() };
    }, {});
  };

  const getFrameAssignmentsForSmallScreen = (extendedFrames) => {
    console.log("Small screen");
    const singlewWindow = extendedFrames.length === 1;
    if (singlewWindow) {
      extendedFrames[0].frame.x += SINGLE_WINDOW_MARGIN_X;
      extendedFrames[0].frame.width -= SINGLE_WINDOW_MARGIN_X*2;
      extendedFrames[0].frame.y += SINGLE_WINDOW_MARGIN_Y;
      extendedFrames[0].frame.height -= SINGLE_WINDOW_MARGIN_Y*2;

      extendedFrames[0].frame.y += SINGLE_WINDOW_OFFSET_Y;
    }

    return extendedFrames.reduce((frames, extendedFrame) => {
      return { ...frames, [extendedFrame.id]: extendedFrame.frame };
    }, {});
  };

  return {
    name: "The Main Layout",

    extends: "tall",

    initialState: {
      mainPaneCount: 1,
    },

    commands: {
      command1: {
        description: "Decrease main pane count",
        updateState: (state) => {
          return {
            ...state,
            mainPaneCount: Math.max(1, state.mainPaneCount - 1),
          };
        },
      },
      command2: {
        description: "Increase main pane count",
        updateState: (state) => {
          return {
            ...state,
            mainPaneCount: state.mainPaneCount + 1,
          };
        },
      },
    },

    getFrameAssignments: (windows, screenFrame, state, extendedFrames) => {
      const isLargeScreen = screenFrame.width >= LARGE_SCREEN_WIDTH_TRHESHOLD;
      if (isLargeScreen) {
        return getFrameAssignmentsForLargeScreen(state, windows, screenFrame);
      } else {
        return getFrameAssignmentsForSmallScreen(extendedFrames);
      }
    },

    updateWithChange: (change, state) => {
      console.log("## Update with change - START ##");
      console.log(JSON.stringify(change, null, 2));
      console.log(JSON.stringify(state, null, 2));
      let newState;
      switch (change.change) {
        case "add":
        case "remove":
        case "window_swap":
          newState = state;
          break;

        default:
          console.log("Unsupported change");
          newState = state;
      }

      console.log("## Update with change - END   ##");
      return newState;
    },
  };
}
