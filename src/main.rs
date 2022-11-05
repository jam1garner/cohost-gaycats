#![feature(path_file_prefix)]
use std::collections::VecDeque;
use std::env;
use std::fs;
use std::path::Path;
use std::path::PathBuf;
use std::process::Command;

use clap::Parser;
use eggbug::{Attachment, Client, Post};
use rand::seq::SliceRandom;
use rand::Rng;
use serde::{Deserialize, Serialize};

const POST_QUEUE_JSON: &str = "post_queue.json";

#[derive(Parser)]
struct Args {
    #[clap(long)]
    refresh_queue: bool,
}

#[derive(Serialize, Deserialize)]
struct State {
    to_post: VecDeque<PathBuf>,
    already_posted: Vec<PathBuf>,
}

impl State {
    fn new() -> Self {
        let mut to_post: Vec<_> = fs::read_dir("cats/")
            .unwrap()
            .map(|image| {
                image
                    .unwrap()
                    .file_name()
                    .to_string_lossy()
                    .into_owned()
                    .into()
            })
            .collect();

        to_post.shuffle(&mut rand::thread_rng());

        Self {
            to_post: to_post.into(),
            already_posted: Vec::new(),
        }
    }

    fn refresh_queue(&mut self) {
        let to_sort = fs::read_dir("cats/").unwrap().map(|image| {
            image
                .unwrap()
                .file_name()
                .to_string_lossy()
                .into_owned()
                .into()
        });

        let to_insert: Vec<_> = to_sort
            .filter(|post| !(self.to_post.contains(post) || self.already_posted.contains(post)))
            .collect();

        let mut rng = rand::thread_rng();

        for post in to_insert {
            let index = rng.gen_range(0..=self.to_post.len());

            self.to_post.insert(index, post);
        }
    }
}

fn try_get_alt_text(path: &Path) -> Option<String> {
    let output = Command::new("python")
        .arg("get_description.py")
        .arg(path)
        .output()
        .ok()?;

    let output = String::from_utf8_lossy(&output.stdout).into_owned();

    if output.is_empty() {
        None
    } else {
        Some(output)
    }
}

#[tokio::main]
async fn main() {
    let args = Args::parse();

    let mut state = fs::read_to_string(POST_QUEUE_JSON)
        .map(|s| serde_json::from_str(&s).ok())
        .ok()
        .flatten()
        .unwrap_or_else(State::new);

    println!("[gaycats] post queue read");

    if args.refresh_queue {
        state.refresh_queue();

        fs::write(POST_QUEUE_JSON, serde_json::to_string(&state).unwrap())
            .expect("Failed to write back post queue to disk");

        println!("[gaycats] post queue updated");
        return;
    }

    let email = env::var("COHOST_EMAIL").expect("Could not log on: COHOST_EMAIL not set");
    let password = env::var("COHOST_PASSWORD").expect("Could not log on: COHOST_PASSWORD not set");
    let page = env::var("COHOST_USERNAME").expect("Could not log on: COHOST_USERNAME not set");

    println!("[gaycats] email/password/username set. authenticating...");

    let client = Client::new();
    let session = client
        .login(&email, &password)
        .await
        .expect("Could not log on: failed to authenticate to cohost");

    println!("[gaycats] session authenticated");

    let image_path = state.to_post.pop_front().unwrap();

    println!("[gaycats] next post retrieved");

    state.already_posted.push(image_path.clone());

    fs::write(POST_QUEUE_JSON, serde_json::to_string(&state).unwrap())
        .expect("Failed to write back post queue to disk");

    println!("[gaycats] post queue written back to disk");

    let cat_name = image_path
        .file_prefix()
        .unwrap()
        .to_string_lossy()
        .into_owned();

    let image_path = Path::new("cats/").join(&image_path);

    println!("[gaycats] image path: {}", image_path.display());

    let content_type = mime_guess::from_path(&image_path)
        .first_or_octet_stream()
        .to_string();

    let alt_text =
        try_get_alt_text(&image_path).unwrap_or_else(|| String::from("A picture of a cat"));

    println!("[gaycats] alt text: \"{}\"", &alt_text);

    let cat = Attachment::new_from_file(&image_path, content_type)
        .await
        .expect("Failed to upload attachment of cat")
        .with_alt_text(alt_text);

    println!("[gaycats] image uploaded");

    let mut post = Post {
        markdown: cat_name,
        attachments: vec![cat],
        tags: vec![String::from("cat"), String::from("cats")],
        draft: false,
        ..Default::default()
    };

    session
        .create_post(&page, &mut post)
        .await
        .expect("Failed to create post");

    println!("[gaycats] post successful");
}
