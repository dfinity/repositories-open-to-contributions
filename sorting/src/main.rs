use std::{
    fs::File,
    io::{prelude::*, BufReader},
    path::Path,
    env,
};

fn lines_from_file(filename: impl AsRef<Path>) -> Vec<String> {
    let file = File::open(filename).expect("no such file");
    let buf = BufReader::new(file);
    buf.lines()
        .map(|l| l.expect("Could not parse line"))
        .collect()
}

fn main() {
    let path = env::var("GITHUB_WORKSPACE").expect("$GITHUB_WORKSPACE is not set");
    let lines = lines_from_file(path + "/open-repositories.txt");
    let mut sorted_lines = lines.clone();
    sorted_lines.sort();

    assert_eq!(lines, sorted_lines)
}
