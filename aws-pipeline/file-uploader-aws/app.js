import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// Directory to read files from
const directoryPath = process.env.DIRECTORY_PATH;

// Desired file extension (e.g., '.txt')
const fileExtension = process.env.FILE_EXTENSION;

// S3 bucket name
const bucketName = process.env.BUCKET_NAME;

// Create an S3 client
const s3Client = new S3Client({
    region: 'us-east-1'
});

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const uploadFile = async (filePath, fileName) => {
    // Read the file content
    fs.readFile(filePath, async (err, data) => {
        if (err) {
            return console.log('Error reading file:', filePath, err);
        }

        // Configure the S3 upload parameters
        const params = {
            Bucket: bucketName,
            Key: fileName, // File name you want to save as in S3
            Body: data
        };

        // Uploading files to the bucket
        try {
            const command = new PutObjectCommand(params);
            const response = await s3Client.send(command);
            console.log(`File uploaded successfully: ${filePath}`);
        } catch (err) {
            console.log('Error uploading file:', filePath, err);
        }
    });
};

const traverseDirectory = (dir) => {
    console.log(`Traversing directory: ${dir}`);
    fs.readdir(dir, (err, files) => {
        if (err) {
            return console.log('Unable to scan directory: ' + err);
        }

        files.forEach(file => {
            const filePath = path.join(dir, file);
            fs.stat(filePath, (err, stats) => {
                if (err) {
                    return console.log('Error stating file:', filePath, err);
                }

                if (stats.isDirectory()) {
                    console.log(`Found directory: ${filePath}`);
                    traverseDirectory(filePath);
                } else if (stats.isFile() && path.extname(file) === fileExtension) {
                    console.log(`Found file: ${filePath}`);
                    uploadFile(filePath, path.relative(directoryPath, filePath));
                }
            });
        });
    });
};

// Start the traversal from the specified directory
traverseDirectory(directoryPath);
