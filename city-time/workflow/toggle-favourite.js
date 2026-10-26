// Run only when Option-Enter is pressed. argv is data, never executable source.
function run(argv) {
    if (argv.length !== 1) throw new Error("Expected the updated favourites list");
    ObjC.import("Foundation");
    const action = ObjC.unwrap($.NSProcessInfo.processInfo.environment.objectForKey("clock_action"));
    const alfred = Application("com.runningwithcrayons.Alfred");
    if (action === "convert") {
        alfred.search("time " + argv[0]);
        return;
    }
    alfred.setConfiguration("favourite_cities", {
        toValue: argv[0],
        inWorkflow: "net.ninjakitty.fast-city-time"
    });
    alfred.search("time ");
}
