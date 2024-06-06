import chokidar from "chokidar";
import path from "path";
import fs from "fs";
import { S3Client, ListObjectsV2Command } from "@aws-sdk/client-s3";

const h5FileDir = "./files_h5";
const metadataFileDir = "./files_metadata";
const bucketName = process.env.BUCKET_NAME;

function searchFile(dir, fileName) {
  // read the contents of the directory
  const files = fs.readdirSync(dir);

  // search through the files
  for (const file of files) {
    // build the full path of the file
    const filePath = path.join(dir, file);

    // get the file stats
    const fileStat = fs.statSync(filePath);

    // if the file is a directory, recursively search the directory
    if (fileStat.isDirectory()) {
      searchFile(filePath, fileName);
    } else if (file.endsWith(fileName)) {
      // if the file is a match, print it
      console.log(filePath);
      return filePath;
    }
  }
}

// Something to use when events are received.
const log = console.log.bind(console);

// Initialize watcher.
const watcher = chokidar.watch(h5FileDir, {
  ignored: /(^|[\/\\])\../, // ignore dotfiles
  persistent: true,
  ignoreInitial: true,
});

watcher
  .on("add", (path) => {
    log(`File ${path} has been added`);
    // parse path to get file name for search
    const pathArray = path.split("/");

    const fileName = pathArray.pop();
    const fileNameNoExt = fileName.replace(".txt", "");
    log(pathArray, fileName, fileNameNoExt);
    // find metadata files
    const newFile = searchFile(metadataFileDir, `${fileNameNoExt}.txt`);
    log("Searched file", newFile);
  })
  .on("change", (path) => log(`File ${path} has been changed`))
  .on("unlink", (path) => log(`File ${path} has been removed`));

// AWS
// Create S3 service object, get credentials from .env file
const client = new S3Client({ region: "us-east-1" });

const input = {
  Bucket: bucketName,
};

(async () => {
  const response = await client.send(new ListObjectsV2Command(input));
  console.log(response);
})();
